from unittest import TestCase

from classes.firebase_db_handler import retrieve_all_notifications, get_notification_by_id, convert_dict_to_card, \
    build_notification_objects
from classes.notification_handler import send_user_notification, get_notification_to_send_json


class TestNotificationHandler(TestCase):

    def test_get_notifications(self):
        notifications = retrieve_all_notifications()
        self.assertGreater(len(notifications), 0)

    def test_convert_dict_to_json(self):
        notifications = retrieve_all_notifications()
        notification_json = convert_dict_to_card(notifications)
        self.assertGreater(len(notification_json), 0)

    def test_build_notification_objects(self):
        notifications = retrieve_all_notifications()
        notification_objects = build_notification_objects(notifications)
        self.assertGreater(len(notification_objects), 0)

    def test_get_notification_by_id(self):

        notification_id_to_send = '0807c3d0-9c9a-472e-a0b6-6831623eb377'
        notification = get_notification_by_id(notification_id_to_send)
        self.assertEqual(notification.id, notification_id_to_send)

    def test_send_notification(self):
        notification_id = '0807c3d0-9c9a-472e-a0b6-6831623eb377'
        send_ids = ['550a92fd-b220-42ca-befe-85d8ba3391bb']
        notification_no_users = get_notification_by_id(notification_id)
        notification_to_send = get_notification_to_send_json(notification_no_users, send_ids)
        return_value = send_user_notification(notification_to_send)
        self.assertEqual(return_value, 200)
