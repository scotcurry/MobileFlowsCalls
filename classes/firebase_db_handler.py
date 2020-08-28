import os
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


def get_auth_cert():
    database_url = 'https://euc-user-uploaddb.firebaseio.com'
    cert_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    firebase_credentials = credentials.Certificate(cert_path)
    firebase_db_app = firebase_admin.initialize_app(firebase_credentials, {
        'databaseURL': database_url
    })
    return firebase_db_app


def get_company_records():
    firebase_db_app = get_auth_cert()
    db_reference = db.reference('/', firebase_db_app)
    db_json = db_reference.get()
    company_count = len(db_json['companies'])
    return company_count


