import json
import unittest
from unittest import TestCase

from classes.firebase_db_handler import get_company_records, add_company, build_company_json
from models.fb_company_information import FbCompanyInformation
from models.fb_user_information import FbUserInformation

class TestFireBaseDBHandler(TestCase):

    def test_check_auth_token(self):
        return_value = get_company_records()
        self.assertEqual(1, return_value)

    def test_add_company(self):
        company_info = FbCompanyInformation('Curryware', '5295 Elmgate Dr.', 'Orchard Lake', '48324')
        company_json = build_company_json(company_info)
        user1 = FbUserInformation('Scot', 'Curry', 'IT', 'Head of IT', None)
        user2 = FbUserInformation('Otis', 'Curry', 'IT', 'Head of Security', 'Curry')
        print(company_json)
        return_value = add_company()
        self.assertEqual(True, return_value)
