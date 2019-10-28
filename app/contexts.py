import os
import logging
import tempfile
import json

from config import config


class GoogleAuthenticationContext:

    def __init__(self, volume_id):
        self.file = None

        volume_settings = config.get_volume_settings(volume_id)
        self.project_id = volume_settings['google_project_id']

        self.section = config.get_google_settings_by_volume_id(volume_id)


    def __enter__(self):
        # create temporary file to store the credentials
        self.file = tempfile.NamedTemporaryFile('w+')

        # write credentials to temporary file
        logging.info('Writing credentials to '+self.file.name)
        json.dump(self.section, self.file)
        self.file.flush()

        os.environ["GOOGLE_PROJECT_ID"] = str(self.project_id)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.file.name

    def __exit__(self ,type, value, traceback):

        self.file.close()

        del os.environ["GOOGLE_PROJECT_ID"]
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

class ResticContext:

    def __init__(self, volume_id):
        self.volume_settings = config.get_volume_settings(volume_id)
        self.cache = config.global_settings['cache']

    def __enter__(self):
        os.environ['RESTIC_REPOSITORY'] = self.volume_settings['remote']
        os.environ['RESTIC_PASSWORD'] = self.volume_settings['password']
        os.environ['XDG_CACHE_HOME'] = self.cache

    def __exit__(self ,type, value, traceback):
        del os.environ["RESTIC_REPOSITORY"]
        del os.environ["RESTIC_PASSWORD"]
        del os.environ['XDG_CACHE_HOME']
