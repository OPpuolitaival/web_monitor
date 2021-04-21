import json
import os
from json import JSONDecodeError


def pytest_addoption(parser):
    parser.addoption("--config", help="Test configration json file")


def pytest_generate_tests(metafunc):
    if "site" in metafunc.fixturenames:
        config_file = metafunc.config.getoption("config")
        if not os.path.isfile(config_file):
            raise Exception('ERROR: {} does not exists!'.format(config_file))
        with open(config_file) as f:
            try:
                sites = json.load(f)['sites']
            except JSONDecodeError as e:
                raise Exception('ERROR: {} is not valid json!'.format(config_file))
            metafunc.parametrize('site', sites, ids=[x['name'] for x in sites])
