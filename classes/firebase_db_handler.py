import json

from slugify import slugify
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

from classes.settings_handler import path_to_settings_file
from models.fb_company_information import FbUserInformation, FbCompanyInformation

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

        company_info.append(FbCompanyInformation(company_name, street_address, city, state, company_employees))
    return company_info


# TODO: Got to get this test to work for the update test.
def retrieve_info_by_company_key(firebase_key):

    all_companies = retrieve_all_company_info()
    for current_company in all_companies:
        if firebase_key == current_company.company_name:
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
    print(path_to_companies)
    response = auth_session.put(path_to_companies, company_json)
    return response.status_code


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



