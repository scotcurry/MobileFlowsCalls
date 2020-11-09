import requests

from models.notification_to_send import NotificationToSend, NotificationToSendEncoder
from models.notification_model import NotificationEncoder
from classes.access_api_handler import get_access_token
from classes.settings_handler import get_settings


def get_notification_to_send_json(notification, user_ids):

    notification_to_convert = NotificationToSend(notification, user_ids)
    return NotificationToSendEncoder().encode(notification_to_convert)


def get_notification_json(notification):
    return NotificationEncoder().encode(notification)


def send_user_notification(notification_json):

    settings_file = 'access_settings.yaml'
    settings = get_settings(settings_file)
    access_url = settings['access_url']
    access_client_id = settings['access_client_id']
    access_client_token = settings['access_token']
    auth_token = get_access_token(access_url, access_client_id, access_client_token)

    auth_token = 'Bearer ' + auth_token
    headers = {'Authorization': auth_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    endpoint = access_url + '/ws1notifications/api/v1/distributed_notifications'
    response = requests.post(url=endpoint, headers=headers, data=notification_json)

    return response.status_code


def build_notification_from_form(form_data, notification):

    title = form_data.get('notification_title')
    description = form_data.get('notification_description')
    image_url = form_data.get('notification_image')

    print(notification.header.title)
    notification.header.title = title
    notification_json = NotificationToSendEncoder().encode(notification)
    return notification_json
