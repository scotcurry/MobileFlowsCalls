class AccessGroup:

    def __init__(self, group_id, group_name):
        self.group_id = group_id
        self.group_name = group_name


class AccessUser:

    def __init__(self, user_name, user_id, display_name, domain):
        self.user_name = user_name
        self.user_id = user_id
        self.display_name = display_name
        self.domain = domain
