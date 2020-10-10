import json
from unittest import TestCase

from classes.firebase_db_handler import get_company_records, add_company, retrieve_company_info, retrieve_company_by_id, \
    get_auth_token, get_company_info_with_session
from classes.upload_page_handler import validate_upload_file_name, validate_file_content
from classes.settings_handler import get_settings, path_to_settings_file
from models.fb_company_information import FbCompanyInformation, FbCompanyInfoEncoder, FbUserInformation, \
    fb_company_decoder


class TestFireBaseDBHandler(TestCase):

    # This tests to make sure there is a good auth token coming back from the Firebase
    def test_check_auth_token(self):
        return_value = get_company_records()
        self.assertGreater(return_value, 0)

    def test_get_with_oauth_token(self):
        companies = get_company_info_with_session()
        print(companies)
        self.assertEqual(1, 1)

    def test_validate_fb_config_file(self):
        path_exists, path_to_file = path_to_settings_file('euc-user-uploaddb-firebase-adminsdk.json')
        self.assertEqual(path_exists, True)

    def test_add_company(self):
        all_users = []
        company_user = FbUserInformation('Jean', 'Mills', 'EDU', 'Retired', None)
        all_users.append(company_user)
        company_user = FbUserInformation('Molly', 'McCann', 'EDU', 'Retired', 'Mills')
        all_users.append(company_user)
        company_info = FbCompanyInformation('Mills Co.', '1 Mills Lane', 'Big Horn', '82121', all_users)
        company_info_json = FbCompanyInfoEncoder().encode(company_info)
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
        company_json = json.loads(retrieved_company)
        company_name = company_json['company_name']
        self.assertEqual(company_name, 'VMware')

    def test_add_user_to_company(self):
        company_id = '-MGJgRfcZE4T-3Ik5Pky'
        company_info_string = retrieve_company_by_id(company_id)
        company_info = json.loads(company_info_string, object_hook=fb_company_decoder)
        new_user = FbUserInformation('Otis', 'Curry', 'Security', 'Head of Security', 'Curry', 'scotc@vmware.com',
                                     'scotcurry4@gmail.com')
        company_info.users.append(new_user)

        self.assertEqual(0, 1)

    def test_file_validation(self):
        return_value = validate_upload_file_name('scot.csv')
        self.assertEqual('valid', return_value)

    def test_file_content(self):
        file_name = 'users.csv'
        return_value = validate_file_content(file_name)
        self.assertNotEqual(10, return_value)
