from flask import Flask, request, redirect, session, url_for, render_template, flash, abort
from werkzeug.utils import secure_filename
from ibm_watson import AssistantV2, ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from datetime import datetime
import logging
import json
import yaml
import os
import msal

# from sn_auth_helper import get_auth_token
from sn_api_calls import get_single_user, get_auth_token
from azure_api_calls import azure_get_token, azure_get_user_info, get_subscription_info

app = Flask(__name__)
# This is a requirement if you are every going to use POSTs and forms.
app.secret_key = os.urandom(24)

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

try:
    with open('settings.yaml', 'r') as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)
except IOError:
    print('Got an IO Error')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def hello_world():
    redirect_url = request.host + '/servicenow'
    files = os.listdir(UPLOAD_FOLDER)
    file_names = []
    total_files_in_uploads = 0

    for current_file in files:
        file_names.append(current_file)
        total_files_in_uploads = len(file_names)
    if request.method == 'GET':
        return render_template('index.html', server_url=redirect_url, number_of_files=total_files_in_uploads,
                               all_files=file_names)
    else:
        button_pushed = request.form['submit_button_process']
        selected_files = request.form.getlist('file')
        print('Total files: ' + str(len(selected_files)))
        return render_template('index.html', server_url=redirect_url, number_of_files=total_files_in_uploads,
                               all_files=file_names)


# See https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html for this complete example
@app.route('/servicenow', methods=['GET', 'POST'])
def service_now():
    # Let's pass the values from a form
    if request.method == 'GET':
        sn_url = settings['sn_server_url']
        sn_api_user = settings['sn_user_name']
        sn_api_user_password = settings['sn_user_password']
        sn_client_id = settings['sn_client_id']
        sn_client_secret = settings['sn_client_secret']
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
        user_sn_name = user_json['result'][0]['user_name']
        user_name = user_json['result'][0]['name']
        user_email = user_json['result'][0]['email']
        return render_template('servicenow.html', user_sn_name=user_sn_name, user_name=user_name, user_email=user_email)


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
    if request.method == 'POST':
        if 'file' not in request.files:
            print('Got no file')
            flash('No File Part')
            return redirect(request.url)
        file = request.files['file']
        print(file.filename)
        if file.filename == '':
            print('filename is blank')
            flash('No Selected File')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            print(os.path.join(UPLOAD_FOLDER, filename))
            print('file saved')

    return render_template('upload.html')


@app.route('/watsoninfo', methods=['GET', 'POST'])
def call_watson():
    if request.method == 'GET':
        assistant_id = 'c5964ff2-fd30-4a23-ae3f-f9a65931d54e'
        ibm_url = 'https://api.us-south.assistant.watson.cloud.ibm.com'
        api_key = 'G14zvFinyuIIUAC3m-z5H3vM_Khjo8wZ6EktagnTEN4n'
        return render_template('watson.html', app_id=assistant_id, ibm_url=ibm_url, api_key=api_key)
    else:
        app_id = request.form['app_id'].strip()
        url = request.form['watson_url'].strip()
        api_key = request.form['api_key'].strip()
        authenticator = IAMAuthenticator(api_key)
        version = '2020-04-01'
        assistant = AssistantV2(version=version, authenticator=authenticator)
        assistant.set_service_url(url)
        print('URL: ' + url)
        print('Assistant ID: ' + app_id)
        print('API Key: ' + api_key)
        response = assistant.create_session(assistant_id=app_id).get_result()
        print(json.dumps(response, indent=2))

        return render_template('watson.html', session_id=response['session_id'])


@app.route('/azure', methods=['GET', 'POST'])
def azure_functions():
    msal_version = msal.__version__
    token = azure_get_token()
    print(token)
    token_to_print = token[0:10] + '...'
    all_users = azure_get_user_info(token)
    subscription_info = get_subscription_info(token)
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


def load_cache():
    cache = msal.SerializableTokenCache()
    if session.get('token_cache'):
        cache.deserialize(session['token_cache'])
    return cache
