from unittest import TestCase

from classes.sn_api_handler import get_auth_token, create_sn_user
from classes.settings_handler import get_settings, path_to_settings_file


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