from urllib.parse import urljoin
import requests
import logging
import yaml

from models.uem_rest_info import UEMServerInfo
from models.uem_user import UEM_User

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)

default_settings = UEMServerInfo('base_uem_url', 'base_oauth_url', 'client_id', 'client_secret')

try:
    with open('settings.yaml', 'r') as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)
        default_settings.base_rest_url = settings['uem_server']
        default_settings.base_oauth_url = settings['uem_oauth_endpoint']
        default_settings.client_id = settings['uem_oauth_client_id']
        default_settings.client_secret = settings['uem_oauth_client_secret']
except IOError:
    logger.error('Got an IO Error reading Settings.yaml')


def get_uem_oauth_token(oauth_url, client_id, client_secret):
    logger.info('UEM OAuth URL: ' + oauth_url)
    logger.info('Client ID: ' + client_id)
    params = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    uem_token_response = requests.post(url=oauth_url, data=params)
    if uem_token_response.status_code != 200:
        logger.error('Error getting UEM Auth Token:')
        return 'Auth Token Error'
    else:
        response_data = uem_token_response.json()
        access_token = response_data['access_token']
        return access_token


def get_uem_users(access_token):
    rest_endpoint = urljoin(default_settings.base_rest_url, 'API/system/users/search')
    auth_string = 'Bearer ' + access_token
    headers = {'Authorization': auth_string, 'Accept': 'application/json', 'Content-Type': 'application/json'}
    returned_users = requests.get(url=rest_endpoint, headers=headers)
    user_data = returned_users.json()
    all_users = []
    for current_user in user_data['Users']:
        all_users.append(UEM_User(current_user['UserName'], current_user['Email']))
    print(len(all_users))
    return all_users
