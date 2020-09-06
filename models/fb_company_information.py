from json import JSONEncoder


class FbCompanyInformation:

    def __init__(self, company_name, street_address, city, state, users):
        self.company_name = company_name
        self.street_address = street_address
        self.company_city = city
        self.company_state = state
        self.users = users


class FbUserInformation:

    def __init__(self, first_name, last_name, department, title, manager_last_name: object):
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.title = title
        self.manager_last_name = manager_last_name


class FbCompanyInfoEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
