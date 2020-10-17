from json import JSONEncoder
from collections import namedtuple


class FbCompanyToActOn:

    def __init__(self, company_nane, company_info):
        self.company_name = company_nane
        self.company_info = company_info


class FbCompanyInformation:

    def __init__(self, company_name, street_address, city, state, users):
        self.company_name = company_name
        self.street_address = street_address
        self.company_city = city
        self.company_state = state
        self.users = users


class FbUserInformation:

    def __init__(self, first_name, last_name, department, title, manager_last_name, corp_email, personal_email: object):
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.title = title
        self.manager_last_name = manager_last_name
        self.corp_email = corp_email
        self.personal_email = personal_email


class FbCompanyInfoEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def fb_company_decoder(fb_company_dict):
    return namedtuple('fb_company_tuple', fb_company_dict.keys())(*fb_company_dict.values())
