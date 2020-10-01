from json import JSONEncoder


class SendGridMessageBody:

    def __init__(self, messages, from_user, content):
        self.personalizations = messages
        self.from_to_convert = from_user
        self.content = content


class SendGridPersonalization:

    def __init__(self, to_users, subject):
        self.to = to_users
        self.subject = subject


class SendGridToUser:
    def __init__(self, email_address, name):
        self.email = email_address
        self.name = name


class SendGridFromUser:
    def __init__(self, email_address, name):
        self.email = email_address
        self.name = name


class SendGridContent:
    def __init__(self, type_to_convert, content_value):
        self.type_to_convert = type_to_convert
        self.value = content_value


class SendGridEmailEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
