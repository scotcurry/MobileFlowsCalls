from urllib.parse import urljoin
import requests
import logging
import json

from models.sn_rest_info import SnServerInfo

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)
cw_settings = SnServerInfo('url', 'client_id', 'client_secret', 'user_name', 'user_password')
default_settings = SnServerInfo('url', 'client_id', 'client_secret', 'user_name', 'user_password')
base_url = ''
UPLOAD_FOLDER = 'uploads'


def get_auth_token(settings):
    url = settings['sn_server_url']
    client_id = settings['sn_client_id']
    client_secret = settings['sn_client_secret']
    user_name = settings['sn_user_name']
    password = settings['sn_user_password']

    params = {'grant_type': 'password', 'client_id': client_id, 'client_secret': client_secret,
              'username': user_name, 'password': password}
    sn_token_response = requests.post(url=url, data=params)
    print('Auth Token POST Status Code: ' + str(sn_token_response.status_code))
    if sn_token_response.status_code != 200:
        return 'Auth Token Error'

    try:
        data = sn_token_response.json()
        logger.info('SN_API_Calls Access Token: ' + data['access_token'])
        return data['access_token']
    except json.decoder.JSONDecodeError:
        return 'JSONDecodeError'


def get_single_user(url, access_token, user_id):
    rest_endpoint = urljoin(url, 'api/now/table/sys_user')
    auth_string = 'Bearer ' + access_token
    headers = {'Authorization': auth_string, 'Accept': 'application/json', 'Content-Type': 'application/json'}
    params = {'sysparm_query': 'user_name=scurry', 'sysparm_limit': '10'}
    returned_user_json = requests.get(url=rest_endpoint, headers=headers, params=params)
    return returned_user_json.json()


# def add_users(csv_file):
#     class_file_path = os.path.dirname(os.path.abspath(__file__))
#     base_path = os.path.split(class_file_path)[0]
#     upload_dir = os.path.join(base_path, UPLOAD_FOLDER)
#     file_name = os.path.join(upload_dir, csv_file)
#
#     successful_adds = 0
#     auth_token = get_auth_token_to_use()
#     if auth_token == 'JSONDecodeError':
#         return 'Error getting Access Token.  Check if hibernating'
#     else:
#         delimiter = '\t'
#         with open(file_name, 'r') as csv_sample_line:
#             first_line = csv_sample_line.readline()
#             if first_line.find(',') > -1:
#                 delimiter = ','
#
#         with open(file_name, newline='') as user_file:
#             user_reader = csv.reader(user_file, delimiter=delimiter)
#             counter = 0
#             for row in user_reader:
#                 if counter > 0:
#                     first_name = row[0].lower()
#                     last_name = row[1].lower()
#                     first_initial = first_name[0:1]
#                     user_name = first_initial + last_name
#                     email_address = user_name + '@vmwareex.com'
#                     logger.info('Adding User: ' + email_address)
#                     success = create_sn_user(auth_token, first_name, last_name, email_address, user_name)
#                     successful_adds = successful_adds + success
#                 counter += 1
#
#    return 'Successful Adds' + str(successful_adds)


def create_sn_user(settings, auth_token, first_name, last_name, email_address, user_name):
    success = 0
    endpoint = settings['add_user_endpoint']
    create_user_info = {'first_name': first_name, 'last_name': last_name, 'email': email_address,
                        'user_name': user_name}
    user_json = json.dumps(create_user_info)
    auth_string = 'Bearer ' + auth_token
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': auth_string}
    if settings['sn_tenant_to_use'] == 'CW':
        endpoint_url = urljoin(settings['cw_sn_server_url'], endpoint)
    else:
        endpoint_url = urljoin(settings['sn_server_url'], endpoint)

    print('URL: ' + endpoint_url)
    print('Auth string: ' + auth_string)
    print('Body: ' + user_json)
    response = requests.post(endpoint_url, headers=headers, data=user_json)
    print('Status code: ' + str(response.status_code))
    if response.status_code != 201:
        logger.error('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        success = -1

    return success
