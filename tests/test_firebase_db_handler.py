import json, uuid
from unittest import TestCase
from slugify import slugify

from classes.firebase_db_handler import get_auth_token, retrieve_info_by_company_key, retrieve_all_company_info, \
    update_company_info, add_company
from classes.upload_page_handler import validate_upload_file_name, validate_file_content
from classes.settings_handler import path_to_settings_file
from models.fb_company_information import FbCompanyInformation, FbCompanyInfoEncoder, FbUserInformation, \
    fb_company_decoder


class TestFireBaseDBHandler(TestCase):

    # This tests to make sure there is a good auth token coming back from the Firebase
    def test_check_auth_token(self):
        auth_token = get_auth_token()
        self.assertNotEqual(auth_token, None)

    def test_add_company(self):
        all_users = []
        # company_user = FbUserInformation('Jean', 'Mills', 'EDU', 'Retired', None, 'jmills@gmail.com',
        #                                  'jmills@curryware.org')
        # all_users.append(company_user)
        # company_user = FbUserInformation('Molly', 'McCann', 'EDU', 'Retired', 'Mills', 'mccann@gmail.com',
        #                                  'mccann@curryware.org')
        company_user = FbUserInformation('Chris', 'Gaidsick', 'Sales', 'SE Manager', None, 'cgaidsick@curryware.org',
                                         'cgaidsick@vmware.com')
        all_users.append(company_user)
        company_user = FbUserInformation('Jen', 'Slabaugh', 'Sales', 'Staff SE', 'Gaidsick', 'jslabaugh@curryware.org',
                                         'jslabaugh@vmware.com')
        all_users.append(company_user)
        company_name = 'VMware'
        normalized_name = slugify(company_name)
        # company_info = FbCompanyInformation(company_name, '1 Mills Lane', 'Big Horn', 'WY', normalized_name, all_users)
        company_info = FbCompanyInformation(company_name, '1155 Perimeter Lane', 'Sandy Springs', 'GA', normalized_name, all_users)
        company_info_json = FbCompanyInfoEncoder().encode(company_info)
        print(company_info_json)
        return_value = add_company(company_info_json, company_info.company_name)
        self.assertEqual(200, return_value)

    def test_update_company(self):
        all_users = []
        # Curryware employees
        # company_user = FbUserInformation('Jean', 'Mills', 'EDU', 'Retired', None, 'jmills@curryware.org',
        #                                  'jmills@vmware.com')
        # all_users.append(company_user)
        # company_user = FbUserInformation('Molly', 'McCann', 'EDU', 'Retired', 'Mills', 'mccann@curryware.org',
        #                                  'mccann@vmware.com')

        company_user = FbUserInformation('Chris', 'Gaidsick', 'Sales', 'SE Manager', None, 'cgaidsick@curryware.org',
                                         'cgaidsick@vmware.com')
        all_users.append(company_user)
        company_user = FbUserInformation('Jen', 'Slabaugh', 'Sales', 'Staff SE', 'Gaidsick', 'jslabaugh@curryware.org',
                                         'jslabaugh@vmware.com')
        all_users.append(company_user)
        # company_info = FbCompanyInformation('Mills Co.', '1 Mills Lane', 'Big Horn', 'WY', all_users)
        company_info = FbCompanyInformation('VMware', '1155 Perimeter Lane', 'Sandy Springs', 'GA', all_users)
        company_info_json = FbCompanyInfoEncoder().encode(company_info)
        print(company_info_json)
        return_value = update_company_info(company_info_json)
        self.assertEqual(200, return_value)

    def test_retrieve_companies(self):
        all_companies = retrieve_all_company_info()
        for current_company in all_companies:
            print(current_company.company_name)
        self.assertGreater(len(all_companies), 0)

    def test_retrieve_company_by_id(self):
        child_index = 'Mills Co.'
        retrieved_company = retrieve_info_by_company_key(child_index)
        self.assertEqual(retrieved_company.company_name, child_index)

    def test_add_user_to_company(self):
        company_id = '-MGJgRfcZE4T-3Ik5Pky'
        company_info_string = retrieve_info_by_company_key(company_id)
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

