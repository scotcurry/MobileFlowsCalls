from flask import Flask, request, redirect, render_template, flash, abort
from werkzeug.utils import secure_filename
from datetime import datetime
from os import path
import logging
import json
import yaml
import os
import msal

# from sn_auth_helper import get_auth_token
# from sn_api_calls import get_single_user, get_auth_token, add_users
from azure_api_calls import azure_get_token, azure_get_user_info
from uem_rest_api import get_uem_oauth_token, get_uem_users
from classes.firebase_db_handler import retrieve_company_info
from classes.upload_page_handler import get_file_list, validate_file_content, add_service_now_users, get_file_path
from classes.sn_api_handler import get_single_user, get_auth_token

app = Flask(__name__)
# This is a requirement if you are every going to use POSTs and forms.
app.secret_key = os.urandom(24)

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# TODO: Need to refactor all of this settings stuff to use the settings_handler.
try:
    with open('settings.yaml', 'r') as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)
except IOError:
    print('Got an IO Error')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index_page():
    redirect_url = request.host + '/servicenow'

    if request.method == 'GET':
        logger.info('Calling GET on index.html')
        all_companies = []
        have_cert_path = False
        if path.exists('./euc-user-uploaddb-firebase-adminsdk.json'):
            print('Path Exists')
            all_companies = retrieve_company_info()
            have_cert_path = True
        return render_template('index.html', all_companies=all_companies, have_cert_path=have_cert_path)
    # else:
    #     logger.info('Calling POST on index.html')
    #     print('Calling POST on index.html')
    #     selected = request.form.get('file')
    #     if 'Process' in request.form['submit']:
    #         print('Processing File')
    #         csv_file = os.path.join(UPLOAD_FOLDER, 'users.csv')
    #         print('CSV File: ' + csv_file)
    #         status_message = add_users(csv_file)
    #     if 'Delete' in request.form['submit']:
    #         if selected is not None:
    #             file_name_to_delete = file_names[int(selected)]
    #             print(file_name_to_delete)
    #             file_to_delete = os.path.join(UPLOAD_FOLDER, file_name_to_delete)
    #             os.remove(file_to_delete)
    #     return render_template('index.html')


@app.route('/uem', methods=['GET', 'POST'])
def uem_calls():
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
    if request.method == 'GET':
        sn_url = settings['cw_sn_server_url']
        sn_api_user = settings['cw_sn_user_name']
        sn_api_user_password = settings['cw_sn_user_password']
        sn_client_id = settings['cw_sn_client_id']
        sn_client_secret = settings['cw_sn_client_secret']
        print()
        return render_template('servicenow.html', sn_client_id=sn_client_id,
                               sn_client_secret=sn_client_secret, sn_api_user_password=sn_api_user_password,
                               sn_api_user=sn_api_user, sn_url=sn_url)
    else:
        url = request.form['sn_url'].strip()
        client_id = request.form['sn_client_id'].strip()
        client_secret = request.form['sn_client_secret'].strip()
        user_name = request.form['sn_api_user_name'].strip()
        user_password = request.form['sn_api_user_password'].strip()
        auth_token = get_auth_token(url, client_id, client_secret, user_name, user_password)
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


@app.route('/uploadcsv', methods=['GET', 'POST'])
def upload_file():
    if request.method =='GET':
        total_files_in_uploads, file_list = get_file_list()
        logger.info('Total files in UPLOADS ' + str(total_files_in_uploads))
        print('Files in upload: ' + str(total_files_in_uploads))
        return render_template('upload.html', number_of_files=total_files_in_uploads, file_list=file_list)

    # Check to see if we have an actual file.
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

        success_statement = 'Success'
        try:
            file_name = file.filename
            filename = secure_filename(file_name)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        except IOError:
            success_statement = 'Failed to upload: ' + filename

    return render_template('file_operation.html', status=success_statement, calling_page='deletecsv')


@app.route('/uploadcsv/<string:file_name>')
def process_user_file(file_name):
    total_files_in_uploads, file_list = get_file_list()
    success_statement = 'Success'
    if validate_file_content(file_name) == 0:
        add_service_now_users(file_name)

    return render_template('file_operation.html', status=success_statement, calling_page='deletecsv')


@app.route('/deletecsv/<string:file_name>')
def delete_user_file(file_name):
    file_to_delete = get_file_path(file_name)
    success_statement = "Success"
    try:
        os.remove(file_to_delete)
    except IOError:
        success_statement = 'Failed to Delete: ' + file_name

    return render_template('file_operation.html', status=success_statement, calling_page='deletecsv')


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


@app.route('/azure', methods=['GET', 'POST'])
def azure_functions():
    msal_version = msal.__version__
    token = azure_get_token()
    print(token)
    token_to_print = token[0:10] + '...'
    all_users = azure_get_user_info(token)
    return render_template('azure.html', msal_version=msal_version, access_token=token_to_print, all_users=all_users)


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
