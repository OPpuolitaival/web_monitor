import requests
import pytest
import time
import logging
import json

logger = logging.getLogger(__name__)

sites = list()
with open('config.json') as f:
    sites = json.load(f)


@pytest.mark.parametrize('name', list(sites))
def test_web_site(name):
    site = sites[name]

    # Do request and measure time
    start_time = time.time()
    r = requests.get(site['url'])
    duration = time.time() - start_time

    # Collect data for kafka
    data = {
        'expected_status_code': site.get('expected_status_code'),
        'status_code': r.status_code,
        'duration': duration,
    }
    logger.debug('data: {}'.format(data))
    assert site.get('expected_status_code') == r.status_code
    if 'assert_text' in list(site):
        assert site['assert_text'] in r.text
