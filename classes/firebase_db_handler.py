import os
import json
import firebase_admin
from firebase_admin import credentials, App
from firebase_admin import db

from models.fb_company_information import FbUserInformation, FbCompanyInformation


def get_auth_cert():
    database_url = 'https://euc-user-uploaddb.firebaseio.com'
    cert_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    firebase_credentials = credentials.Certificate(cert_path)
    firebase_db_app: App = firebase_admin.initialize_app(firebase_credentials, {
        'databaseURL': database_url
    })
    return firebase_db_app


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
    db_reference = db.reference('companies', firebase_db_app)
    fb_companies = db_reference.order_by_key().get()
    all_companies_json = []
    for key, val in fb_companies.items():
        all_companies_json.append(val)

    company_info = []
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
                                                       employee_title, employee_manager))
        company_name = current_company_json['company_name']
        street_address = current_company_json['street_address']
        city = current_company_json['company_city']
        state = current_company_json['company_state']

        company_info.append(FbCompanyInformation(company_name, street_address, city, state, company_employees))
    return company_info
