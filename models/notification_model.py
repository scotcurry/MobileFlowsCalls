from json import JSONEncoder


class NotificationPayload:

    def __init__(self, header, body, image_url, actions, notification_id, notification_name):
        self.header = header
        self.body = body
        self.image = image_url
        self.actions = actions
        self.id = notification_id
        self.name = notification_name


class NotificationImage:

    def __init__(self, url):
        self.href = url


class NotificationAction:

    def __init__(self, action_id, label, action_type, primary, allow_repeated, image_url, action_key, completed_label):
        self.id = action_id
        self.label = label
        self.type = action_type
        self.primary = primary
        self.allow_repeated = allow_repeated
        self.url = image_url
        self.action_key = action_key
        self.completed_label = completed_label


class NotificationTitle:

    def __init__(self, title):
        self.title = title


class NotificationBody:

    def __init__(self, description):
        self.description = description


class NotificationEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
