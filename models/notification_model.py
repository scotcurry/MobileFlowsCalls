from json import JSONEncoder


class NotificationPayload:

    def __init__(self, header, body, image_url, actions, id):
        self.header = header
        self.body = body
        self.image = image_url
        self.actions = actions
        self.id = id


class NotificationImage:

    def __init__(self, url):
        self.href = url


class NotificationAction:

    def __init__(self, action_id, label, action_type, primary, allow_repeated, image_url, action_key):
        self.id = action_id
        self.label = label
        self.type = action_type
        self.primary = primary
        self.allow_repeated = allow_repeated
        self.url = image_url
        self.action_key = action_key


class NotificationTitle:

    def __init__(self, title):
        self.title = title


class NotificationBody:

    def __init__(self, description):
        self.description = description


class NotificationEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
