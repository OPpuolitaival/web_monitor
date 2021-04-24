"""
Tests for web site monitoring
"""

import logging
import time

import pytest
import requests

logger = logging.getLogger(__name__)

@pytest.mark.web_page_monitoring
def test_get_url(site, send_to_kafka):
    """ Executes HTTP get method for given site
        Example of site dict:
        {
            "name": "google",
            "url": "https://google.com",
            "expected_return_code": 200,
            "assert_text": "google"
        }
    """
    # Do request and measure time
    start_time = time.time()
    response = requests.get(site['url'])
    duration = time.time() - start_time

    # Collect data for kafka
    data = {
        'url': site['url'],
        'return_code': response.status_code,
        'expected_return_code': site.get('expected_return_code'),
        'duration': duration * 1000,
        'content_length': len(response.text),  # Sometimes this helps to see that things changes
        'start_time': start_time,
        'content_check': True
    }
    logger.debug('data: %s', data)
    send_to_kafka(data)

    assert site.get('expected_return_code') == response.status_code
    if 'assert_text' in list(site):
        assert site['assert_text'] in response.text
