# This is the link to the sample code for this.  https://github.com/AzureAD/microsoft-authentication-library-for-python
# Permissions must be set in App Registration in Azure, and for this to work it needs to be Application type
# permission.
import logging
import msal
import json
import requests

from models.azure_user import Azure_User

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.ERROR)
logger = logging.getLogger(__name__)

try:
    with open('azure_settings.json', 'r') as azure_settings:
        config = json.load(azure_settings)
except IOError:
    print('Got an Azure IO Error')

azure_client_id = config['client_id']
authority = None
azure_client_secret = config['secret']
azure_scope = config['scope']


def azure_get_token():
    token_to_return = 'No Token Retrieved.  See Logs'
    cache = msal.SerializableTokenCache()
    msal_app = msal.ConfidentialClientApplication(config['client_id'], authority=config['authority'],
                                                  client_credential=azure_client_secret, token_cache=cache)
    result = msal_app.acquire_token_silent(config['scope'], account=None)
    if not result:
        logging.info('Not suitable token')
        result = msal_app.acquire_token_for_client(scopes=config['scope'])

    if 'access_token' in result:
        token_to_return = result['access_token']
    else:
        logger.error(result.get('error'))
        logger.error(result.get('error_description'))
        logger.error(result.get('correlation_id'))

    return token_to_return


def azure_get_user_info(access_token):
    headers = {'Authorization': 'Bearer ' + access_token}
    user_data = requests.get(config['user_endpoint'], headers=headers)
    user_json = user_data.json()
    print(user_json)
    all_users = user_json['value']
    all_user_list = []
    domain_to_search = 'vmwareex.com'
    for current_user in all_users:
        user_to_add = Azure_User(current_user['displayName'], current_user['mail'], current_user['jobTitle'],
                                 current_user['mobilePhone'])
        all_user_list.append(user_to_add)

    return all_user_list
