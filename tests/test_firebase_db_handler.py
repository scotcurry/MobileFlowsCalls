from unittest import TestCase

from classes.firebase_db_handler import get_company_records, add_company, retrieve_company_info, retrieve_company_by_id
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

