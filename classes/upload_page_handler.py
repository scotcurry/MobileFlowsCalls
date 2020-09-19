import os

UPLOAD_FOLDER = 'uploads'


def get_file_list():
    total_files_in_uploads = 0
    file_names = []
    file_ids = []
    if os.path.exists(UPLOAD_FOLDER):
        files = os.listdir(UPLOAD_FOLDER)

        total_files_in_uploads = 0
        file_counter = 0
        status_message = 'Unknown Status'
        for current_file in files:
            file_names.append(current_file)
            file_ids.append('file' + str(file_counter))
            total_files_in_uploads = len(file_names)
            file_counter = total_files_in_uploads
    else:
        os.mkdir(UPLOAD_FOLDER)

    return total_files_in_uploads, file_names
