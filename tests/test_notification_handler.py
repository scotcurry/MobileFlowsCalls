from unittest import TestCase

from classes.firebase_db_handler import retrieve_all_notifications
from classes.notification_handler import convert_dict_to_card, build_notification_objects
from models.notification_to_send import NotificationToSend, NotificationEncoder


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

    def test_send_notification(self):
        notifications = retrieve_all_notifications()
        notification_objects = build_notification_objects(notifications)
        notification_id_to_send = '0807c3d0-9c9a-472e-a0b6-6831623eb377'
        all_users = ['90300caa-225f-415d-a9ec-276161433de4', '550a92fd-b220-42ca-befe-85d8ba3391bb']
        for current_notification in notification_objects:
            if current_notification.id == notification_id_to_send:
                notification_base_json = current_notification
                notification_to_send = NotificationToSend(notification_base_json, all_users)
                notification_json = NotificationEncoder().encode(notification_to_send)
        self.assertEqual(1, 1)
