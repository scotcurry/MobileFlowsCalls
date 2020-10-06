import json
import base64
import requests

from classes.settings_handler import get_settings
from models.access_models import AccessGroup, AccessUser


def get_access_info():
    settings_file = 'access_settings.yaml'
    settings = get_settings(settings_file)
    client_id = settings['access_client_id']
    access_token = settings['access_token']
    access_url = settings['access_url']
    auth_token = get_access_token(access_url, client_id, access_token)
    auth_token = 'HZN ' + auth_token
    return access_url, auth_token;


def get_access_token(access_url, client_id, access_token):

    string_to_encode = client_id + ':' + access_token
    string_to_encode_bytes = string_to_encode.encode('ascii')
    base64_bytes = base64.b64encode(string_to_encode_bytes)
    base64_string = base64_bytes.decode('ascii')
    auth_header = 'Basic ' + base64_string

    auth_endpoint = '/SAAS/auth/oauthtoken'
    url_endpoint = access_url + auth_endpoint

    headers = {'Authorization': auth_header, 'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'grant_type': 'client_credentials'}
    response = requests.post(url_endpoint, headers=headers, params=params)
    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json['access_token']
    else:
        access_token = 'Error'

    return access_token


def get_all_groups():

    server_url, auth_token = get_access_info()
    headers = {'Authorization': auth_token}
    url_endpoint = server_url + '/SAAS/jersey/manager/api/scim/Groups'

    response = requests.get(url=url_endpoint, headers=headers)
    all_groups = []
    if response.status_code == 200:
        response_json = response.json()
        groups = response_json['Resources']
        for group in groups:
            group_id = group['id']
            group_name = group['displayName']
            all_groups.append(AccessGroup(group_id, group_name))

    return all_groups


def get_group_id_by_name(group_name):

    server_url, auth_token = get_access_info()
    headers = {'Authorization': auth_token}
    url_endpoint = server_url + '/SAAS/jersey/manager/api/scim/Groups'
    response = requests.get(url=url_endpoint, headers=headers)
    group_id = ''
    if response.status_code == 200:
        response_json = response.json()
        groups = response_json['Resources']
        for group in groups:
            if group['displayName'] == group_name:
                group_id = group['id']

    return group_id


def get_users_in_group(group_id):

    server_url, auth_token = get_access_info()
    end_point = '/SAAS/jersey/manager/api/scim/Groups/' + group_id
    url_endpoint = server_url + end_point
    headers = {'Authorization': auth_token}
    response = requests.get(url=url_endpoint, headers=headers)
    users_in_group = []
    if response.status_code == 200:
        response_json = response.json()
        all_members = response_json['members']
        for member in all_members:
            user_id = member['value']
            display_name = member['display']
            current_user = AccessUser(None, user_id, display_name, None, None, None, None)
            users_in_group.append(current_user)

    return users_in_group


def get_all_user_attributes(user_id):

    server_url, auth_token = get_access_info()
    endpoint = '/SAAS/jersey/manager/api/scim/Users/'
    url_endpoint = server_url + endpoint + user_id
    headers = {'Authorization': auth_token}
    response = requests.get(url=url_endpoint, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        user_name = response_json['userName']
        user_id = response_json['id']
        first_name = response_json['name']['givenName']
        last_name = response_json['name']['familyName']
        display_name = first_name + ' ' + last_name
        email_address = response_json['emails'][0]['value']
        sam_account_name = response_json['urn:scim:schemas:extension:workspace:tenant:aw-curryware-ex1:1.0']['sAMAccountName']
        user_domain = response_json['urn:scim:schemas:extension:workspace:1.0']['domain']
        upn = response_json['urn:scim:schemas:extension:workspace:1.0']['userPrincipalName']
        user_info = AccessUser(user_name, user_id, display_name, user_domain, email_address, sam_account_name, upn)
        return user_info
    else:
        error_info = AccessUser('NlaAdZiCLo', None, None, None, None, None, None)
        return error_info


def set_new_hire_group(group_id):

    server_url, auth_token = get_access_info()
    one_day = 86400000
    body_dict = {'enabled': True, 'userAttributeForEmail': 'emails', 'loginLinkValidityMillis': one_day,
                 'groupUuid': group_id}
    post_body = json.dumps(body_dict)
    endpoint = '/SAAS/jersey/manager/api/token/auth/configuration'
    url_endpoint = server_url + endpoint
    headers = {'Authorization': auth_token,
               'Content-Type': 'application/vnd.vmware.horizon.manager.token.auth.configuration+json',
               'Accept': 'application/vnd.vmware.horizon.manager.token.auth.configuration+json'}
    response = requests.post(url=url_endpoint, data=post_body, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        is_enabled = response_json['enabled']
        return 'Success'
    else:
        return str(response.status_code)


def create_magic_link(username, domain):

    server_url, auth_token = get_access_info()
    body_dict = {'domain': domain, 'userName': username}
    post_body = json.dumps(body_dict)
    print(post_body)
    endpoint = '/SAAS/jersey/manager/api/token/auth/state'
    url_endpoint = server_url + endpoint
    headers = {'Authorization': auth_token,
               'Content-Type': 'application/vnd.vmware.horizon.manager.tokenauth.generation.request+json',
               'Accept': 'application/vnd.vmware.horizon.manager.tokenauth.link.response+json'}
    response = requests.post(url=url_endpoint, data=post_body, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        login_link = response_json['loginLink']
    elif response.status_code == 409:
        login_link = 'User Exists'
    else:
        login_link = 'Error'

    return login_link


def delete_magic_link_token(user_id):

    access_server, auth_token = get_access_info()
    endpoint = '/SAAS/jersey/manager/api/token/auth/state/'
    url_endpoint = access_server + endpoint + user_id
    headers = {'Authorization': auth_token}
    response = requests.delete(url=url_endpoint, headers=headers)
    if response.status_code == 204:
        return_value = 'Success'
    else:
        return_value = str(response.status_code)

    return return_value
