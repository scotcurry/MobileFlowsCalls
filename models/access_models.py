class AccessGroup:

    def __init__(self, group_id, group_name):
        self.group_id = group_id
        self.group_name = group_name


class AccessUser:

    def __init__(self, user_name, user_id, display_name, domain, email_address, sam_account_name, upn, mail_nickname):
        self.user_name = user_name
        self.user_id = user_id
        self.display_name = display_name
        self.domain = domain
        self.email_address = email_address
        self.sam_account_name = sam_account_name
        self.upn = upn
        self.mail_nickname = mail_nickname
