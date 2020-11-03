from json import JSONEncoder


class NotificationToSend:

    def __init__(self, notification_body, user_ids):
        self.notification_card = notification_body
        self.user_ids = user_ids


class NotificationToSendEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
