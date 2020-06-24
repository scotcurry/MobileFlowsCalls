from flask import session
from urllib.parse import urljoin
import requests
import logging
import csv
import yaml
import json

from models.sn_rest_info import SnServerInfo

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)
cw_settings = SnServerInfo('url', 'client_id', 'client_secret', 'user_name', 'user_password')
default_settings = SnServerInfo('url', 'client_id', 'client_secret', 'user_name', 'user_password')
base_url = ''

try:
    with open('settings.yaml', 'r') as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)
        cw_settings.base_url = settings['cw_sn_server_url']
        cw_settings.client_id = settings['cw_sn_client_id']
        cw_settings.client_secret = settings['cw_sn_client_secret']
        cw_settings.user_name = settings['cw_sn_user_name']
        cw_settings.user_password = settings['cw_sn_user_password']

        default_settings.base_url = settings['sn_server_url']
        default_settings.client_id = settings['sn_client_id']
        default_settings.client_secret = settings['sn_client_secret']
        default_settings.user_name = settings['sn_user_name']
        default_settings.user_password = settings['sn_user_password']
except IOError:
    print('Got an IO Error')


def get_auth_token(url, client_id, client_secret, user_name, password):
    params = {'grant_type': 'password', 'client_id': client_id, 'client_secret': client_secret,
              'username': user_name, 'password': password}
    sn_token_response = requests.post(url=url, data=params)
    print(sn_token_response.status_code)
    if sn_token_response.status_code != 200:
        return 'Got an Error'

    data = sn_token_response.json()
    logger.error('SN_API_Calls Access Token: ' + data['access_token'])
    session['access_token'] = data['access_token']
    return data['access_token']


def get_single_user(url, access_token, user_id):
    rest_endpoint = urljoin(url, 'api/now/table/sys_user')
    auth_string = 'Bearer ' + access_token
    headers = {'Authorization': auth_string, 'Accept': 'application/json', 'Content-Type': 'application/json'}
    params = {'sysparm_query': 'user_name=scurry', 'sysparm_limit': '10'}
    returned_user_json = requests.get(url=rest_endpoint, headers=headers, params=params)
    return returned_user_json.json()


def add_users(csv_file):
    auth_token = get_auth_token_to_use()
    with open(csv_file, newline='') as user_file:
        user_reader = csv.reader(user_file, delimiter='\t')
        counter = 0
        for row in user_reader:
            if counter > 0:
                first_name = row[0].lower()
                last_name = row[1].lower()
                first_initial = first_name[0:1]
                user_name = first_initial + last_name
                email_address = user_name + '@vmwareex.com'
                print(email_address)
                create_sn_user(auth_token, first_name, last_name, email_address, user_name)
            counter += 1
            print(counter)

    return True


def create_sn_user(auth_token, first_name, last_name, email_address, user_name):
    endpoint = settings['add_user_endpoint']
    create_user_info = {'first_name': first_name, 'last_name': last_name, 'email': email_address,
                        'user_name': user_name}
    user_json = json.dumps(create_user_info)
    auth_string = 'Bearer ' + auth_token
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': auth_string}
    if settings['sn_tenant_to_use'] == 'CW':
        endpoint_url = urljoin(cw_settings.base_url, endpoint)
    else:
        endpoint_url = urljoin(default_settings.base_url, endpoint
                               )
    print('Endpoint URL: ' + endpoint_url)
    print('Auth String: ' + auth_string)
    print('User Info: ' + user_json)
    response = requests.post(endpoint_url, headers=headers, data=user_json)
    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
    else:
        print('Success')

    return True


def get_auth_token_to_use():
    if settings['sn_tenant_to_use'] == 'CW':
        auth_token = get_auth_token(cw_settings.base_url, cw_settings.client_id, cw_settings.client_secret,
                                    cw_settings.user_name, cw_settings.user_password)
        return auth_token
    else:
        auth_token = get_auth_token(default_settings.base_url, default_settings.client_id,
                                    default_settings.client_secret, default_settings.user_name,
                                    default_settings.user_password)
        return auth_token
