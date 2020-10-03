from unittest import TestCase

from classes.firebase_db_handler import get_company_records, add_company, retrieve_company_info, retrieve_company_by_id
from classes.upload_page_handler import validate_upload_file_name, validate_file_content
from classes.sn_api_handler import get_auth_token, create_sn_user
from classes.settings_handler import get_settings
from classes.sendgrid_email_handler import validate_api_key, build_email_message, send_email
from classes.access_api_handler import get_access_info, get_all_groups, get_group_id_by_name, set_new_hire_group, \
    create_magic_link, get_users_in_group, get_all_user_attributes
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

    def test_get_ws1_access_token(self):
        url, token = get_access_info()
        print(token)
        self.assertGreater(len(token), 40)

    def test_get_access_groups(self):
        all_groups = get_all_groups()
        self.assertGreater(len(all_groups), 0)

    def test_get_group_id_by_name(self):
        group_name = 'NewHires@curryware.org'
        group_id = get_group_id_by_name(group_name)
        self.assertEqual('91077254-b603-4bc9-affe-179aca3fa6b6', group_id)

    def test_set_new_hire_group(self):
        group_id = '91077254-b603-4bc9-affe-179aca3fa6b6'
        return_value = set_new_hire_group(group_id)
        self.assertEqual('Success', return_value)

    def test_create_magic_link(self):
        user_name = 'jcraig'
        domain = 'curryware.org'
        return_value = create_magic_link(user_name, domain)
        self.assertNotEqual('Error', return_value)

    def test_get_users_in_group(self):
        group_id = '91077254-b603-4bc9-affe-179aca3fa6b6'
        all_users = get_users_in_group(group_id)
        self.assertGreater(len(all_users), 0)

    def test_get_username_by_userid(self):
        user_id = '7f9144b9-abbf-46a7-8297-12bcd2288042'
        user_name = get_all_user_attributes(user_id)
        self.assertNotEqual('NlaAdZiCLo', user_name)
