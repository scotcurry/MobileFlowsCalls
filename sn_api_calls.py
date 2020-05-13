from flask import session
from urllib.parse import urljoin
import requests
import logging

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)


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
