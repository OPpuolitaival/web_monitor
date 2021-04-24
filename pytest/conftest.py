"""
Pytest configuration
"""

import json
import os
from json import JSONDecodeError

pytest_plugins = [
    "lib.fixtures",
]


def pytest_addoption(parser):
    """ Add commandline options """
    parser.addoption("--config", help="Test configration json file")


def pytest_generate_tests(metafunc):
    """ Parametrize tests based on commandline given configuration file """
    if "site" in metafunc.fixturenames:
        config_file_path = metafunc.config.getoption("config")
        if not os.path.isfile(config_file_path):
            raise Exception('ERROR: {} does not exists!'.format(config_file_path))
        with open(config_file_path) as config_file:
            try:
                sites = json.load(config_file)['sites']
            except JSONDecodeError as error:
                raise Exception('ERROR: {} is not valid json!'.format(config_file_path)) from error
            metafunc.parametrize('site', sites, ids=[x['name'] for x in sites])
