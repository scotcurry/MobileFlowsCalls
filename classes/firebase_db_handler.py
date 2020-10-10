import json
import firebase_admin
from firebase_admin import credentials, db

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


def get_company_info_with_session():

    auth_session = get_auth_token()
    path_to_companies = database_name + 'companies.json'
    response = auth_session.get(path_to_companies)
    return response.json()


def get_auth_cert():
    database_url = 'https://euc-user-uploaddb.firebaseio.com'
    path_exists, settings_file_path = path_to_settings_file('euc-user-uploaddb-firebase-adminsdk.json')
    if path_exists:
        try:
            firebase_admin.get_app()
        except ValueError:
            print('firebase_db_handler - get_auth_cert - Got ValueError exception')
            firebase_credentials = credentials.Certificate(settings_file_path)
            firebase_admin.initialize_app(firebase_credentials, {
                'databaseURL': database_url
            })
    else:
        print("Not credential file")
    return firebase_admin.get_app()


def get_company_records():
    firebase_db_app = get_auth_cert()
    db_reference = db.reference('/', firebase_db_app)
    db_json = db_reference.get()
    company_count = len(db_json['companies'])
    return company_count


def add_company(company_json):
    firebase_db_app = get_auth_cert()
    db_reference = db.reference('/', firebase_db_app)
    db_reference.child('companies').push(company_json)
    return True


def retrieve_company_info():
    firebase_db_app = get_auth_cert()
    company_info = []
    if firebase_db_app is not None:
        db_reference = db.reference('companies', firebase_db_app)
        fb_companies = db_reference.order_by_key().get()
        all_companies_json = []
        for key, val in fb_companies.items():
            print(key)
            all_companies_json.append(val)

        for current_company in all_companies_json:
            current_company_json = json.loads(current_company)
            company_employees = []
            for current_user in current_company_json['users']:
                employee_first_name = current_user['first_name']
                employee_last_name = current_user['last_name']
                employee_department = current_user['department']
                employee_title = current_user['title']
                employee_manager = current_user['manager_last_name']
                company_employees.append(FbUserInformation(employee_first_name, employee_last_name, employee_department,
                                                           employee_title, employee_manager, None, None))
            company_name = current_company_json['company_name']
            street_address = current_company_json['street_address']
            city = current_company_json['company_city']
            state = current_company_json['company_state']

            company_info.append(FbCompanyInformation(company_name, street_address, city, state, company_employees))

    return company_info


def retrieve_company_by_id(child_id):
    firebase_db_app = get_auth_cert()
    db_location = 'companies/' + child_id
    db_reference = db.reference(db_location, firebase_db_app)
    company_to_retrieve = db_reference.get()
    print(company_to_retrieve)
    return company_to_retrieve
