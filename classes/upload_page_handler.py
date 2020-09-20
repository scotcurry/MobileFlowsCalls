import os
import re
import csv
from pathvalidate import validate_filename, ValidationError

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
    class_file_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.split(class_file_path)[0]
    upload_dir = os.path.join(base_path, UPLOAD_FOLDER)
    file_name = os.path.join(upload_dir, file_name)
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
                first_name = row[0]
                result = re.match(character_pattern, first_name)
                if result:
                    return_code = 100
                last_name = row[1]
                result = re.match(character_pattern, last_name)
                if result:
                    return_code = 100

    return return_code
