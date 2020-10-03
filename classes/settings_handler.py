import os
import yaml


def get_settings(settings_file_name):
    try:
        class_file_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.split(class_file_path)[0]
        settings_file = os.path.join(base_path, settings_file_name)
        # print('settings_handler.py - get_settings - Path to settings: ' + settings_file)
        with open(settings_file, 'r') as settings_file:
            settings = yaml.load(settings_file, Loader=yaml.FullLoader)
    except IOError as error:
        print('Got an IO Error: ' + error.description)

    return settings
