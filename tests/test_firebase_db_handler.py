from unittest import TestCase

from classes.firebase_db_handler import get_company_records, add_company, retrieve_company_info, retrieve_company_by_id
from classes.upload_page_handler import validate_upload_file_name, validate_file_content
from classes.sn_api_handler import get_auth_token, create_sn_user
from classes.settings_handler import get_settings
from classes.sendgrid_email_handler import validate_api_key, build_email_message, send_email
from models.fb_company_information import FbCompanyInformation, FbCompanyInfoEncoder, FbUserInformation


class TestFireBaseDBHandler(TestCase):

    # This tests to make sure there is a good auth token coming back from the Firebase
    def test_check_auth_token(self):
        return_value = get_company_records()
        self.assertGreater(return_value, 0)

    def test_add_company(self):
        all_users = []
        company_user = FbUserInformation('Jean', 'Mills', 'EDU', 'Retired', None)
        all_users.append(company_user)
        company_user = FbUserInformation('Molly', 'McCann', 'EDU', 'Retired', 'Mills')
        all_users.append(company_user)
        company_info = FbCompanyInformation('Mills Co.', '1 Mills Lane', 'Big Horn', '82121', all_users)
        company_info_json = FbCompanyInfoEncoder().encode(company_info)
        print(company_info_json)
        add_company(company_info_json)
        self.assertEqual(1, 1)

    def test_retrieve_companies(self):
        all_companies = retrieve_company_info()
        for current_company in all_companies:
            print(current_company.company_name)
        self.assertGreater(len(all_companies), 0)

    def test_retrieve_company_by_id(self):
        child_index = '-MGJgRfcZE4T-3Ik5Pky'
        retrieved_company = retrieve_company_by_id(child_index)
        self.assertEqual(1, 1)

    def test_file_validation(self):
        return_value = validate_upload_file_name('scot.csv')
        self.assertEqual('valid', return_value)

    def test_file_content(self):
        file_name = 'users.csv'
        return_value = validate_file_content(file_name)
        self.assertNotEqual(10, return_value)

    def test_get_settings(self):
        settings = get_settings()
        self.assertEqual('default', settings['sn_tenant_to_use'])

    def test_get_sn_auth_token(self):
        settings = get_settings()
        auth_token = get_auth_token(settings)
        auth_token_size = len(auth_token)
        self.assertEqual(86, auth_token_size)

    def test_create_sn_user(self):
        settings = get_settings()
        auth_token = get_auth_token(settings)
        have_success = create_sn_user(settings, auth_token, 'Doug', 'Lange', 'dlange@unittest.com', 'dlange')
        self.assertEqual(0, have_success)

    def test_send_email_api_key(self):
        return_value = validate_api_key()
        self.assertEqual('Success', return_value)

    def test_build_email_message(self):
        messages = build_email_message('Scot Curry', 'scotc@vmware.com', 'Scot Curryware', 'scurry@curryware.org',
                                       'An email message', 'text/plain', 'Hello World')
        return_value = send_email(messages)
        self.assertEqual(200, return_value)