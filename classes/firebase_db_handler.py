import json

from slugify import slugify
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

from classes.settings_handler import path_to_settings_file
from models.fb_company_information import FbUserInformation, FbCompanyInformation
from models.notification_model import NotificationTitle, NotificationBody, NotificationImage, NotificationAction, \
    NotificationPayload
from models.tenant_info import TenantInfo

database_name = 'https://euc-user-uploaddb.firebaseio.com/'


def get_auth_token():

    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/firebase.database"
    ]

    path_exists, settings_file_path = path_to_settings_file('euc-user-uploaddb-firebase-adminsdk.json')
    auth_credentials = service_account.Credentials.from_service_account_file(settings_file_path, scopes=scopes)
    auth_session = AuthorizedSession(credentials=auth_credentials)

    return auth_session


def retrieve_all_company_info():

    auth_session = get_auth_token()
    path_to_companies = database_name + 'companies.json'
    response = auth_session.get(path_to_companies)
    response_json = response.json()
    all_companies_json = []
    company_info = []
    for key, val in response_json.items():
        all_companies_json.append(val)

        for current_company in all_companies_json:
            company_employees = []
            for current_user in current_company['users']:
                employee_first_name = current_user['first_name']
                employee_last_name = current_user['last_name']
                employee_department = current_user['department']
                employee_title = current_user['title']
                if 'manager_last_name' in current_user:
                    employee_manager = current_user['manager_last_name']
                else:
                    employee_manager = None
                company_employees.append(FbUserInformation(employee_first_name, employee_last_name, employee_department,
                                                           employee_title, employee_manager, None, None))

        company_name = current_company['company_name']
        street_address = current_company['street_address']
        city = current_company['company_city']
        state = current_company['company_state']
        normalized_name = current_company['normalized_name']

        company_info.append(FbCompanyInformation(company_name, street_address, city, state, normalized_name, company_employees))
    return company_info


# TODO: Got to get this test to work for the update test.
def retrieve_info_by_company_key(firebase_key):

    all_companies = retrieve_all_company_info()
    for current_company in all_companies:
        if firebase_key == current_company.normalized_name:
            return current_company

    return None


def update_company_info(company_info_json):

    auth_session = get_auth_token()
    path_to_companies = database_name + 'companies.json'
    response = auth_session.patch(path_to_companies, company_info_json)
    return response.status_code


def add_company(company_json, company_name):

    auth_session = get_auth_token()
    normalized_name = slugify(company_name)
    path_to_companies = database_name + 'companies/' + normalized_name + '.json'
    response = auth_session.put(path_to_companies, company_json)
    return response.status_code


def retrieve_all_notifications():

    auth_session = get_auth_token()
    path_to_notifications = database_name + 'notifications.json'
    result = auth_session.get(path_to_notifications)
    notifications_json = result.json()
    return notifications_json


def get_notification_by_id(notification_id):

    notifications = retrieve_all_notifications()
    notification_objects = build_notification_objects(notifications)
    for current_notification in notification_objects:
        if current_notification.id == notification_id:
            return current_notification
    return None


def build_notification_objects(notifications):

    all_notifications = []
    for key, value in notifications.items():
        json_payload = json.dumps(value)
        current_notification = json.loads(json_payload)
        title = NotificationTitle(current_notification['header']['title'])
        body = NotificationBody(current_notification['body']['description'])
        image = NotificationImage(current_notification['image']['href'])
        notification_id = current_notification['id']
        notification_name = key

        all_actions = []
        if 'actions' in current_notification:
            for current_action_key, current_action_value in current_notification['actions'].items():
                action_id = current_notification['actions'][current_action_key]['id']
                action_key = current_notification['actions'][current_action_key]['action_key']
                action_completed_label = current_notification['actions'][current_action_key]['completed_label']
                action_label = current_notification['actions'][current_action_key]['label']
                action_primary = current_notification['actions'][current_action_key]['primary']
                action_type = current_notification['actions'][current_action_key]['type']
                action_url = NotificationImage(current_notification['actions'][current_action_key]['url']['href'])
                action_allow_repeated = current_notification['actions'][current_action_key]['allow_repeated']
                action_info = NotificationAction(action_id, action_label, action_type, action_primary,
                                                 action_allow_repeated, action_url, action_key, action_completed_label)
                all_actions.append(action_info)

        notification_payload = NotificationPayload(title, body, image, all_actions, notification_id, notification_name)
        all_notifications.append(notification_payload)

    return all_notifications


def update_firebase_notification_record(notification_number, update_json):

    auth_session = get_auth_token()
    notification_number = database_name + 'notifications/' + notification_number + '.json'
    response = auth_session.put(notification_number, update_json)
    return response.status_code


def get_tenant_info():

    auth_session = get_auth_token()
    tenant_node = database_name + 'tenant_info' + '.json'
    tenants = auth_session.get(tenant_node)

    all_tenants = []
    if tenants.status_code == 200:
        tenant_json = tenants.json()
        for key, value in tenant_json.items():
            tenant_name = tenant_json[key]['tenant_name']
            tenant_id = tenant_json[key]['tenant_id']
            access_url = tenant_json[key]['access_url']
            client_id = tenant_json[key]['access_client_id']
            client_token = tenant_json[key]['access_token']
            new_hire_group_name = tenant_json[key]['new_hire_group']

            tenant_to_add = TenantInfo(tenant_id, tenant_name, access_url, client_id, client_token, new_hire_group_name)
            all_tenants.append(tenant_to_add)
    else:
        return None

    return all_tenants


def get_tenant_info_by_id(tenant_id):

    all_tenants = get_tenant_info()
    tenant_to_return = None
    for current_tenant in all_tenants:
        if current_tenant.tenant_id == tenant_id:
            tenant_to_return = current_tenant

    return tenant_to_return


def get_tenant_new_hire_group(tenant_id):

    all_tenants = get_tenant_info()
    group_to_return = None
    for current_tenant in all_tenants:
        if current_tenant.tenant_id == tenant_id:
            group_to_return = current_tenant.new_hire_group_name

    return group_to_return
