"""
Configuration Module

Data is loaded from a JSON file and make accessible via module-level
properties, e.g. (import config; config.<key>)

"""

import json
import sys


CONFIG_FILENAME = 'config.json'


def UnknownConfigKeys(ks):
    raise Exception(('Keys {} do not exist in the current '
                    'config. If you want to create new keys, add them '
                    'directly to the file: {}')
                    .format(ks, CONFIG_FILENAME))

_config = {}


def _load():
    """Init the local config object from a JSON file.
    """
    global _config
    _config.update(json.load(open(CONFIG_FILENAME, 'rb')))


def get(k):
    """Return a config value. Let it fail if key not set.
    """
    if k not in _config:
        raise UnknownConfigKeys([k])
    return _config[k]


# Load config from file on module import.
_load()
