import os
import re
import csv
from pathvalidate import validate_filename, ValidationError
from classes.sn_api_handler import get_auth_token, create_sn_user
from classes.settings_handler import get_settings

UPLOAD_FOLDER = 'uploads'


def get_file_list():
    total_files_in_uploads = 0
    file_names = []
    file_ids = []
    if os.path.exists(UPLOAD_FOLDER):
        files = os.listdir(UPLOAD_FOLDER)

        total_files_in_uploads = 0
        file_counter = 0
        for current_file in files:
            file_names.append(current_file)
            file_ids.append('file' + str(file_counter))
            total_files_in_uploads = len(file_names)
            file_counter = total_files_in_uploads
    else:
        os.mkdir(UPLOAD_FOLDER)

    return total_files_in_uploads, file_names


def validate_upload_file_name(file_name):

    return_value = 'valid'
    try:
        validate_filename(file_name)
    except ValidationError as error:
        return_value = error.description
        print(error.description)

    print(file_name)
    return return_value


def validate_file_content(file_name):

    return_code = 0
    # class_file_path = os.path.dirname(os.path.abspath(__file__))
    # base_path = os.path.split(class_file_path)[0]
    # upload_dir = os.path.join(base_path, UPLOAD_FOLDER)
    file_name = get_file_path(file_name)
    print(file_name)

    delimiter = '\t'
    with open(file_name, 'r') as csv_sample_line:
        first_line = csv_sample_line.readline()
        if first_line.find(',') > -1:
            delimiter = ','

    with open(file_name, newline='') as user_file:
        user_reader = csv.reader(user_file, delimiter=delimiter)
        counter = 0
        character_pattern = '[^a-zA-Z]'
        for row in user_reader:
            if counter > 0:
                counter = counter + 1
                first_name = row[0]
                result = re.match(character_pattern, first_name)
                if result:
                    return_code = 100
                last_name = row[1]
                result = re.match(character_pattern, last_name)
                if result:
                    return_code = 100

    return return_code


def add_service_now_users(filename):

    file_to_process = get_file_path(filename)
    delimiter = '\t'
    with open(file_to_process, 'r') as csv_sample_line:
        first_line = csv_sample_line.readline()
        if first_line.find(',') > -1:
            delimiter = ','

    settings = get_settings()
    auth_token = get_auth_token(settings)
    total_successful = 0
    with open(file_to_process, newline='') as user_file:
        user_reader = csv.reader(user_file, delimiter=delimiter)
        for row in user_reader:
            first_name = row[0]
            last_name = row[1]
            user_name = first_name[0:1].lower() + last_name.lower()
            email_address = user_name + '@vmwareex.com'
            success = create_sn_user(settings, auth_token, first_name, last_name, email_address, user_name)
            if success == 0:
                total_successful = total_successful + 1
    return total_successful


def get_file_path(file_name):

    class_file_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.split(class_file_path)[0]
    upload_dir = os.path.join(base_path, UPLOAD_FOLDER)
    file_name = os.path.join(upload_dir, file_name)

    return file_name
