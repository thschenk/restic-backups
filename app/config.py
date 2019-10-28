

import json
import operator

class Config:

    def __init__(self):
        self.global_settings = {}


    def load_json_config(self, filename):
        with open(filename) as fd:
            self._data = json.load(fd)

    def get_volume_settings(self, volume_id):
        for volume in self._data['volumes']:
            if volume['id']==volume_id:
                return volume

        raise Exception('Can not find volume settings for '+repr(volume_id))


    def all_volume_ids(self):
        return list(map(operator.itemgetter('id'), self._data['volumes']))


    def get_google_settings_by_volume_id(self, volume_id):
        volume_settings = self.get_volume_settings(volume_id)
        google_key = volume_settings['google_key']

        try:
            return self._data['google_keys'][google_key]
        except KeyError:
            raise KeyError('No configuration section found for google key '+repr(google_key))


# initialise a global config
config = Config()
