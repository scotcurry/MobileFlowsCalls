from flask import Flask, request, redirect, render_template, flash, abort, url_for, send_file, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from datetime import datetime
import logging
import json
import os

# from sn_auth_helper import get_auth_token
# from sn_api_calls import get_single_user, get_auth_token, add_users
# from azure_api_calls import azure_get_token, azure_get_user_info
from uem_rest_api import get_uem_oauth_token, get_uem_users
from classes.firebase_db_handler import retrieve_all_company_info, retrieve_info_by_company_key,\
    retrieve_all_notifications, get_notification_by_id, build_notification_objects, get_tenant_info, \
    get_tenant_new_hire_group
from classes.upload_page_handler import get_file_list, validate_file_content, add_service_now_users, get_file_path
from classes.sn_api_handler import get_single_user, get_auth_token
from classes.access_api_handler import get_users_in_group, get_all_user_attributes, create_magic_link, \
    delete_magic_link_token, get_group_id_by_name, get_all_groups
from classes.settings_handler import get_settings
from classes.sendgrid_email_handler import build_email_message, send_email, html_email_builder
from classes.notification_handler import get_notification_to_send_json, send_user_notification, \
    build_notification_from_form
from ddtrace import tracer

app = Flask(__name__)
# This is a requirement if you are every going to use POSTs and forms.
app.secret_key = os.urandom(24)

tracer.configure(hostname='datadog-agent', port='8126')

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# TODO:  Need to update this once I have the tenant select screen working.
def index_page():

    all_tenants = get_tenant_info()
    if request.method == 'GET':
        logger.info('Calling Index Page')
        return render_template('index.html', all_tenants=all_tenants)
    else:
        # Environment is the tenant_id field in the Firebase database.
        environment = request.form.get('environment')
        session['tenant_id'] = environment
        return redirect(url_for('company_info_page', tenant_id=environment))


@app.route('/company_info', methods=['GET', 'POST'])
def company_info_page():

    all_companies = retrieve_all_company_info()
    tenant_id = session['tenant_id']
    print('company_info_page - tenant_id ' + tenant_id)
    if request.method == 'GET':
        logger.info('Calling GET on company_info.html')
        return render_template('company_info.html', all_companies=all_companies)
    else:
        button_value = request.form['action_button']
        if button_value[0: 4] == 'edit':
            company_to_edit = button_value[4:]
            print('Company to edit: ' + company_to_edit)
            return redirect(url_for('add_edit_company', company_to_edit=company_to_edit))


@app.route('/add_edit_company', methods=['GET', 'POST'])
def add_edit_company():

    firebase_key = request.args['company_to_edit']
    print('add_edit_firebase_key ' + firebase_key)
    company_info = retrieve_info_by_company_key(firebase_key)
    company_users = company_info.users
    if request.method == 'GET':
        return render_template('add_edit_company.html', company_info=company_info, company_users=company_users,
                               action='edit')
    if request.method == 'POST':
        action_button_text = request.form['action_button']
        if action_button_text == 'update_company':
            company_name = request.form['company_name']
            street_address = request.form['street_address']
            city = request.form['city']
            print(street_address)
        return render_template('add_edit_company.html', company_info=company_info, company_users=company_users,
                               action='edit')


@app.route('/uploadcsv', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        total_files_in_uploads, file_list = get_file_list()
        logger.info('Total files in UPLOADS ' + str(total_files_in_uploads))
        print('Files in upload: ' + str(total_files_in_uploads))
        return render_template('upload.html', number_of_files=total_files_in_uploads, file_list=file_list)

    # Check to see if we have an actual file.
    success_statement = 'Success'
    if request.method == 'POST':
        if 'file' not in request.files:
            print('Got no file')
            flash('No File Part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('filename is blank')
            flash('No Selected File')
            return redirect(request.url)

        filename = None
        try:
            file_name = file.filename
            filename = secure_filename(file_name)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        except IOError:
            success_statement = 'Failed to upload: ' + filename

    return render_template('file_operation.html', status=success_statement, calling_page='deletecsv')


@app.route('/uploadcsv/<string:file_name>')
def uploaded_file_process(file_name):
    success_statement = 'Success'
    if validate_file_content(file_name) == 0:
        add_service_now_users(file_name)

    return render_template('file_operation.html', status=success_statement, calling_page='deletecsv')


@app.route('/zero_day', methods=['GET', 'POST'])
def handle_zero_day():

    tenant_id = session['tenant_id']
    if request.method == 'GET':
        all_groups = get_all_groups(tenant_id)
        return render_template('all_groups.html', all_groups=all_groups)
    else:
        return render_template("company_info.html")


@app.route('/zero_day/<string:group_id>')
def set_zero_day_configuration(group_id):

    tenant_id = session['tenant_id']
    all_users = get_users_in_group(tenant_id, group_id)
    user_display_info = []
    for current_user in all_users:
        user_info = get_all_user_attributes(tenant_id, current_user.user_id)
        user_display_info.append(user_info)

    return render_template('zero_day_users.html', all_users=user_display_info)


@app.route('/send_email/<string:user_id>')
def send_zero_day_email(user_id):

    tenant_id = session['tenant_id']
    user_info = get_all_user_attributes(tenant_id, user_id)
    link_to_send = create_magic_link(tenant_id, user_info.user_name, user_info.domain)
    return_value = 'Failure'
    if link_to_send[0: 4] == 'http':
        from_address = 'scurry@curryware.org'
        from_name = 'Welcome Admin'
        subject = 'Welcome Email'
        content_type = 'text/html'
        email_body = html_email_builder(link_to_send, user_info.user_name, user_info.display_name)
        email_json = build_email_message(user_info.display_name, user_info.email_address, from_name, from_address,
                                         subject, content_type, email_body)
        return_value = send_email(email_json)
        if return_value == '200' or return_value == '202':
            return_value = 'Success'

    return render_template('file_operation.html', status=return_value)


@app.route('/delete_token/<string:user_id>')
def delete_auth_token(user_id):

    tenant_id = session['tenant_id']
    return_value = delete_magic_link_token(tenant_id, user_id)
    return render_template('file_operation.html', status=return_value)


@app.route('/notifications', methods=['GET', 'POST'])
def notification_page():

    firebase_notifications = retrieve_all_notifications()
    notifications = build_notification_objects(firebase_notifications)
    return render_template('notifications.html', all_notifications=notifications)


@app.route('/send_notification/<string:notification_id>', methods=['GET', 'POST'])
def send_notification(notification_id):

    notification = get_notification_by_id(notification_id)
    tenant_id = session['tenant_id']
    group_name = get_tenant_new_hire_group(tenant_id)
    new_user_group_id = get_group_id_by_name(tenant_id, group_name)
    if request.method == 'GET':
        all_users = get_users_in_group(tenant_id, new_user_group_id)
        return render_template('send_notification.html', notification=notification, all_users=all_users)
    else:
        send_ids = request.form.getlist('user_id')
        notification_no_users = get_notification_by_id(notification_id)
        notification_to_send = get_notification_to_send_json(notification_no_users, send_ids)
        return_value = send_user_notification(notification_to_send)
        if return_value == 200:
            return render_template('file_operation.html', status='Success')
        else:
            return render_template('file_operation.html', status=str(return_value))


@app.route('/notification_detail/<string:notification_id>', methods=['GET', 'POST'])
def display_notification_detail(notification_id):

    notification = get_notification_by_id(notification_id)
    if request.method == 'GET':
        action_count = len(notification.actions)
        print('app - display_notification_detail -' + str(action_count))
        return render_template('notification_detail.html', notification=notification, action_count=action_count)
    else:
        form_data = request.form
        return_value = build_notification_from_form(form_data, notification)
        print(return_value)
        return render_template('file_operation.html', status='Success')


@app.route('/notification_images/<string:image_name>')
def get_image(image_name):

    path = 'notification_images/' + image_name
    return send_file(path, mimetype='image/png')


@app.route('/uem', methods=['GET', 'POST'])
def uem_calls():
    settings = get_settings('settings.yaml')
    if request.method == "GET":
        uem_oauth_url = settings['uem_oauth_endpoint']
        uem_client_id = settings['uem_oauth_client_id']
        uem_client_secret = settings['uem_oauth_client_secret']
        return render_template('uem.html', uem_oauth_url=uem_oauth_url, uem_client_id=uem_client_id,
                               uem_client_secret=uem_client_secret)
    else:
        uem_oauth_url = request.form['uem_oauth_url'].strip()
        uem_client_id = request.form['uem_client_id'].strip()
        uem_client_secret = settings['uem_oauth_client_secret']
        oauth_token = get_uem_oauth_token(uem_oauth_url, uem_client_id, uem_client_secret)
        uem_users = get_uem_users(oauth_token)
        return render_template('uem.html', uem_oauth_url=uem_oauth_url, uem_client_id=uem_client_id,
                               uem_client_secret=uem_client_secret, uem_users=uem_users)


# See https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html for this complete example
@app.route('/servicenow', methods=['GET', 'POST'])
def service_now():
    # Let's pass the values from a form
    settings = get_settings('settings.yaml')
    if request.method == 'GET':
        sn_url = settings['cw_sn_server_url']
        sn_api_user = settings['cw_sn_user_name']
        sn_api_user_password = settings['cw_sn_user_password']
        sn_client_id = settings['cw_sn_client_id']
        sn_client_secret = settings['cw_sn_client_secret']
        return render_template('servicenow.html', sn_client_id=sn_client_id,
                               sn_client_secret=sn_client_secret, sn_api_user_password=sn_api_user_password,
                               sn_api_user=sn_api_user, sn_url=sn_url)
    else:
        url = request.form['sn_url'].strip()
        auth_token = get_auth_token(settings)
        user_json = get_single_user(url, auth_token, 'scurry')
        print(user_json)
        user_name = user_json['result'][0]['name']
        user_email = 'place_holder'
        return render_template('servicenow.html', user_sn_name=user_name, user_name=user_name, user_email=user_email)


@app.route('/appapproval', methods=['GET', 'POST'])
def appapproval():
    if request.method == 'GET':
        app_id = 'appapproval'
        namespace = '478698'
        service_now_url = 'https://dev90402.service-now.com'
        return render_template('appapproval.html', app_id=app_id, namespace=namespace, servicenow_url=service_now_url)
    else:
        app_id = request.form['app_id'].strip()
        namespace = request.form['namespace'].strip()
        return render_template('appapproval.html', app_id=app_id, namespace=namespace)


@app.route('/about', methods=['GET'])
def about():
    server = request.url
    base_url = request.base_url
    return render_template('about.html', server=server, base_url=base_url)


@app.route('/deletecsv/<string:file_name>')
def delete_user_file(file_name):
    file_to_delete = get_file_path(file_name)
    success_statement = "Success"
    try:
        os.remove(file_to_delete)
    except IOError:
        success_statement = 'Failed to Delete: ' + file_name

    return render_template('file_operation.html', status=success_statement, calling_page='deletecsv')


# @app.route('/azure', methods=['GET', 'POST'])
# def azure_functions():
#     msal_version = msal.__version__
#     token = azure_get_token()
#     print(token)
#     token_to_print = token[0:10] + '...'
#     all_users = azure_get_user_info(token)
#     return render_template('azure.html', msal_version=msal_version, access_token=token_to_print, all_users=all_users)


@app.route('/getipaddress', methods=['POST'])
def get_ad_ip_address():
    if not request.json:
        abort(400)
    now = datetime.now()
    json_time = now.strftime('%Y-%m-%d %H:%M:%S')
    try:
        file_to_save = {
            'update_time': json_time,
            'ip_address': request.json['ip_address']
        }
        file_name = 'ip_address.json'
        path = os.path.join(UPLOAD_FOLDER, file_name)
        print(path)
        print(file_to_save)
        with open(path, 'w') as output:
            output.write(json.dumps(file_to_save))
    except IOError as e:
        print(e)
        return 'Did Not Save'
    return file_to_save


def allowed_file(filename):
    print(filename)
    print(filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(HTTPException)
def handle_bad_request(exception):
    response = exception.get_response()
    response.data = json.dumps({
        'code': exception.code,
        'name': exception.name,
        'description': exception.description
    })
    logger.error(response.data)

# @app.route('/watsoninfo', methods=['GET', 'POST'])
# def call_watson():
#     if request.method == 'GET':
#         assistant_id = 'c5964ff2-fd30-4a23-ae3f-f9a65931d54e'
#         ibm_url = 'https://api.us-south.assistant.watson.cloud.ibm.com'
#         api_key = 'G14zvFinyuIIUAC3m-z5H3vM_Khjo8wZ6EktagnTEN4n'
#         return render_template('watson.html', app_id=assistant_id, ibm_url=ibm_url, api_key=api_key)
#     else:
#         app_id = request.form['app_id'].strip()
#         url = request.form['watson_url'].strip()
#         api_key = request.form['api_key'].strip()
#         authenticator = IAMAuthenticator(api_key)
#         version = '2020-04-01'
#         assistant = AssistantV2(version=version, authenticator=authenticator)
#         assistant.set_service_url(url)
#         print('URL: ' + url)
#         print('Assistant ID: ' + app_id)
#         print('API Key: ' + api_key)
#         response = assistant.create_session(assistant_id=app_id).get_result()
#         print(json.dumps(response, indent=2))
#
#         return render_template('watson.html', session_id=response['session_id'])
