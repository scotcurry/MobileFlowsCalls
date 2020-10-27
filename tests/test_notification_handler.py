from unittest import TestCase

from classes.firebase_db_handler import retrieve_all_notifications
from classes.notification_handler import convert_dict_to_card, build_notifications


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
        notification_json = convert_dict_to_card(notifications)
        notification_objects = build_notifications(notification_json)
        self.assertGreater(len(notification_objects), 0)