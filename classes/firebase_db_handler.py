import os
import json
import firebase_admin
from firebase_admin import credentials, App
from firebase_admin import db


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


def add_company():
    firebase_db_app = get_auth_cert()
    db_reference = db.reference('/', firebase_db_app)
    return True


def build_company_json(company_info):
    company_dict = {'company_name': company_info.company_name, 'company_address': company_info.street_address,
                    'company_city': company_info.company_city, 'company_state': company_info.company_state}
    company_json = json.dumps(company_dict, cls=dict)
    return company_json
