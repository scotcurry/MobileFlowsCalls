import os
import requests
from classes.settings_handler import get_settings, path_to_static_folder
from models.sendgrid_email import SendGridContent, SendGridToUser, SendGridFromUser, SendGridMessageBody, \
    SendGridEmailEncoder, SendGridPersonalization


def validate_api_key():

    bearer_token = get_authorization_header()
    headers = {'Authorization': bearer_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    endpoint = 'https://api.sendgrid.com/v3/api_keys'
    response = requests.get(url=endpoint, headers=headers)
    response_code = response.status_code
    print(response_code)
    if response_code == 200:
        return 'Success'
    else:
        return 'Failure'


def build_email_message(to_name, to_email_address, from_name, from_email_address, subject, content_type, content_value):
    to_user = SendGridToUser(to_email_address, to_name)
    all_users = [to_user]
    personalization = SendGridPersonalization(all_users, subject)
    all_personalizations = [personalization]
    from_user = SendGridFromUser(from_email_address, from_name)
    content = SendGridContent(content_type, content_value)
    all_content = [content]
    email_bodies = SendGridMessageBody(all_personalizations, from_user, all_content)
    json = SendGridEmailEncoder().encode(email_bodies)
    json = json.replace('from_to_convert', 'from')
    json = json.replace('type_to_convert', 'type')
    return json


def send_email(messages_json):
    endpoint = 'https://api.sendgrid.com/v3//mail/send'
    api_key = get_authorization_header()
    auth_header = {'Authorization': api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    print(messages_json)
    print(auth_header)
    response = requests.post(url=endpoint, data=messages_json, headers=auth_header)
    print('sendgrid_email - send_email - Status Code: ' + str(response.status_code))
    if response.status_code == 200 or response.status_code == 202:
        return str(200)
    else:
        return str(response.status_code)


def get_authorization_header():
    settings = get_settings('sendgrid_settings.yaml')
    sendgrid_api_key = settings['sendgrid_api_key']
    bearer_token = 'Bearer ' + sendgrid_api_key

    return bearer_token


def html_email_builder(link_to_send, first_name, username):

    email_body = '<h2>New Hire Email</h2>'
    email_body = email_body + '<a href="' + link_to_send + '">Auth Token</a>'
    static_folder = path_to_static_folder()
    email_template_file = os.path.join(static_folder + '/email_template.html')
    print(first_name)
    print(username)
    with open(email_template_file, 'r') as email_template:
        email_template_text = email_template.read()
        print(email_template_text.find('{Access_URL}'))
        email_template_text = email_template_text.replace('{Access_URL}', link_to_send)
        email_template_text = email_template_text.replace('{Username}', username)
        email_template_text = email_template_text.replace('{FirstName}', first_name)
    return email_template_text
