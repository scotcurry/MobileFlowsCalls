import json

from slugify import slugify
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

from classes.settings_handler import path_to_settings_file
from models.fb_company_information import FbUserInformation, FbCompanyInformation
from models.notification_model import NotificationTitle, NotificationBody, NotificationImage, NotificationAction, \
    NotificationPayload

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

    all_notifications = retrieve_all_notifications()
    for key, value in all_notifications.items():
        json_to_parse = value
        if json_to_parse['id'] == notification_id:
            title = NotificationTitle(json_to_parse['header']['title'])
            body = NotificationBody(json_to_parse['body']['description'])
            image = NotificationImage(json_to_parse['image']['href'])
            action_nodes = json_to_parse['actions']
            all_actions = []
            for current_action in action_nodes:
                action_key = json_to_parse['actions'][current_action]['action_key']
                allow_repeated = json_to_parse['actions'][current_action]['allow_repeated']
                completed_label = json_to_parse['actions'][current_action]['completed_label']
                action_id = json_to_parse['actions'][current_action]['id']
                action_label = json_to_parse['actions'][current_action]['label']
                primary = json_to_parse['actions'][current_action]['primary']
                action_type = json_to_parse['actions'][current_action]['type']
                url = json_to_parse['actions'][current_action]['url']['href']
                build_notification = NotificationAction(action_id, action_label, action_type, primary, allow_repeated,
                                                        url, action_key, completed_label)
                all_actions.append(build_notification)

            notification_to_return = NotificationPayload(title, body, image, all_actions, None)

    return notification_to_return


def get_notification_by_id(notification_id):

    notifications = retrieve_all_notifications()
    notification_objects = build_notification_objects(notifications)
    for current_notification in notification_objects:
        if current_notification.id == notification_id:
            return current_notification
    return None


def build_notification_objects(notifications):

    notification_dict = convert_dict_to_card(notifications)
    all_notifications = []
    for json_payload in notification_dict:
        current_notification = json.loads(json_payload)
        title = NotificationTitle(current_notification['header']['title'])
        body = NotificationBody(current_notification['body']['description'])
        image = NotificationImage(current_notification['image']['href'])
        notification_id = current_notification['id']

        all_actions = []
        for key, value in current_notification['actions'].items():
            action_id = current_notification['actions'][key]['id']
            action_key = current_notification['actions'][key]['action_key']
            action_completed_label = current_notification['actions'][key]['completed_label']
            action_label = current_notification['actions'][key]['label']
            action_primary = current_notification['actions'][key]['primary']
            action_type = current_notification['actions'][key]['type']
            action_url = NotificationImage(current_notification['actions'][key]['url']['href'])
            action_allow_repeated = current_notification['actions'][key]['allow_repeated']
            action_info = NotificationAction(action_id, action_label, action_type, action_primary,
                                             action_allow_repeated, action_url, action_key, action_completed_label)
            all_actions.append(action_info)

        notification_payload = NotificationPayload(title, body, image, all_actions, notification_id)
        all_notifications.append(notification_payload)

    return all_notifications


def convert_dict_to_card(notifications):

    all_notifications = []
    for key, value in notifications.items():
        all_notifications.append(json.dumps(value))
    return all_notifications


# def get_auth_cert():
#     database_url = 'https://euc-user-uploaddb.firebaseio.com'
#     path_exists, settings_file_path = path_to_settings_file('euc-user-uploaddb-firebase-adminsdk.json')
#     if path_exists:
#         try:
#             firebase_admin.get_app()
#         except ValueError:
#             print('firebase_db_handler - get_auth_cert - Got ValueError exception')
#             firebase_credentials = credentials.Certificate(settings_file_path)
#             firebase_admin.initialize_app(firebase_credentials, {
#                 'databaseURL': database_url
#             })
#     else:
#         print("Not credential file")
#     return firebase_admin.get_app()


# def get_company_records():
#     firebase_db_app = get_auth_cert()
#     db_reference = db.reference('/', firebase_db_app)
#     db_json = db_reference.get()
#     company_count = len(db_json['companies'])
#     return company_count


# def add_company(company_json):
#     firebase_db_app = get_auth_cert()
#     db_reference = db.reference('/', firebase_db_app)
#     db_reference.child('companies').push(company_json)
#     return True


# def retrieve_company_info():
#     firebase_db_app = get_auth_cert()
#     company_info = []
#     if firebase_db_app is not None:
#         db_reference = db.reference('companies', firebase_db_app)
#         fb_companies = db_reference.order_by_key().get()
#         all_companies_json = []
#         for key, val in fb_companies.items():
#             print(key)
#             all_companies_json.append(val)
#
#         for current_company in all_companies_json:
#             current_company_json = json.loads(current_company)
#             company_employees = []
#             for current_user in current_company_json['users']:
#                 employee_first_name = current_user['first_name']
#                 employee_last_name = current_user['last_name']
#                 employee_department = current_user['department']
#                 employee_title = current_user['title']
#                 employee_manager = current_user['manager_last_name']
#                 company_employees.append(FbUserInformation(employee_first_name, employee_last_name, employee_department,
#                                                            employee_title, employee_manager, None, None))
#             company_name = current_company_json['company_name']
#             street_address = current_company_json['street_address']
#             city = current_company_json['company_city']
#             state = current_company_json['company_state']
#
#             company_info.append(FbCompanyInformation(company_name, street_address, city, state, company_employees))
#
#     return company_info



