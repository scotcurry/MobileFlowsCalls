import json
import base64
import requests

from models.notification_model import NotificationTitle, NotificationAction, NotificationBody, NotificationEncoder, \
    NotificationImage, NotificationPayload
from models.notification_to_send import NotificationToSend


def convert_dict_to_card(notifications):

    all_notifications= []
    for key, value in notifications.items():
        all_notifications.append(json.dumps(value))
    return all_notifications


def build_notification_objects(notifications):

    notification_dict = convert_dict_to_card(notifications)
    all_notifications = []
    for json_payload in notification_dict:
        current_notification = json.loads(json_payload)
        title = NotificationTitle(current_notification['header']['title'])
        body = NotificationBody(current_notification['body']['description'])
        image = NotificationImage(current_notification['image']['href'])
        notification_id = current_notification['id']

        all_actions = []
        for key, value in current_notification['actions'].items():
            action_id = current_notification['actions'][key]['id']
            action_key = current_notification['actions'][key]['action_key']
            action_completed_label = current_notification['actions'][key]['completed_label']
            action_label = current_notification['actions'][key]['label']
            action_primary = current_notification['actions'][key]['primary']
            action_type = current_notification['actions'][key]['type']
            action_url = current_notification['actions'][key]['url']['href']
            action_allow_repeated = current_notification['actions'][key]['allow_repeated']
            action_info = NotificationAction(action_id, action_label, action_type, action_primary,
                                             action_allow_repeated, action_url, action_key)
            all_actions.append(action_info)

        notification_payload = NotificationPayload(title, body, image, all_actions, notification_id)
        all_notifications.append(notification_payload)

    return all_notifications
