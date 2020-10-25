from unittest import TestCase

from classes.sendgrid_email_handler import validate_api_key, build_email_message, send_email
from classes.access_api_handler import get_access_info, get_all_groups, get_group_id_by_name, set_new_hire_group, \
    create_magic_link, get_users_in_group, get_all_user_attributes, delete_magic_link_token, check_if_new_hire_group
from classes.settings_handler import path_to_static_folder


class TestAccessCalls(TestCase):

    def test_send_email_api_key(self):
        return_value = validate_api_key()
        self.assertEqual('Success', return_value)

    def test_build_email_message(self):
        messages = build_email_message('Scot Curry', 'scotc@vmware.com', 'Scot Curryware', 'scurry@curryware.org',
                                       'An email message', 'text/plain', 'Hello World')
        print(messages)
        return_value = send_email(messages)
        self.assertEqual('200', return_value)

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
        user_id = '550a92fd-b220-42ca-befe-85d8ba3391bb'
        user_info = get_all_user_attributes(user_id)
        self.assertNotEqual('NlaAdZiCLo', user_info.user_name)

    def test_get_magic_link(self):
        user_id = '550a92fd-b220-42ca-befe-85d8ba3391bb'
        user_info = get_all_user_attributes(user_id)
        email_link = create_magic_link(user_info.user_name, user_info.domain)
        print(email_link)
        is_http = email_link[0: 4]
        self.assertEqual(is_http, 'http')

    def test_build_auth_link_email(self):
        from_address = 'scurry@curryware.org'
        from_name = 'Welcome Admin'
        subject = 'Welcome Email'
        content_type = 'text/plain'
        user_id = '550a92fd-b220-42ca-befe-85d8ba3391bb'
        # delete_magic_link_token(user_id)
        user_info = get_all_user_attributes(user_id)
        email_link = create_magic_link(user_info.user_name, user_info.domain)
        email_json = build_email_message(user_info.display_name, user_info.mail_nickname, from_name, from_address,
                                         subject, content_type, email_link)
        print(email_json)
        status_code = send_email(email_json)
        self.assertEqual(status_code, '200')

    def test_delete_auth_token(self):
        user_id = '550a92fd-b220-42ca-befe-85d8ba3391bb'
        return_value = delete_magic_link_token(user_id)
        self.assertEqual('Success', return_value)

    def test_is_new_hire_enabled(self):
        enabled_group_id = '91077254-b603-4bc9-affe-179aca3fa6b6'
        not_enabled_group_id = 'b66a4a09-6d07-4aab-b187-93933dbc3c79'
        return_value = check_if_new_hire_group(enabled_group_id)
        print('True return - ' + str(return_value))
        if return_value:
            true_valid = True
        return_value = check_if_new_hire_group(not_enabled_group_id)
        print(return_value)
        if not return_value:
            false_valid = True
        value_to_compare = true_valid and false_valid
        print('False return - ' + str(return_value))
        self.assertEqual(True, value_to_compare)

    def test_get_static_folder(self):
        folder_path = path_to_static_folder()
        print(folder_path)
        self.assertGreater(len(folder_path), 15)