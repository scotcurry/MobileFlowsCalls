import unittest
from unittest import TestCase

from classes.firebase_db_handler import get_company_records


class TestFireBaseDBHandler(TestCase):

    def test_check_auth_token(self):
        return_value = get_company_records()
        self.assertEqual(1, return_value)
