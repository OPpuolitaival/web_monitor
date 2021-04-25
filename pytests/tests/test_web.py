"""
Tests for web site monitoring
"""

import logging
import re
import time

import pytest
import requests

logger = logging.getLogger(__name__)


def regex_search(regex, text):
    """
    Do regular expression search for text.

    :param regex: Regular expression for search, if none then disabled
    :param text: Text where to search
    :return: True if search finds something or regex is None
    """
    if regex:
        return re.search(regex, text) is not None
    return True


@pytest.mark.web_page_monitoring
def test_get_url(site, send_to_kafka):
    """ Executes HTTP get method for given site
        Example of site dictionary:
        {
          "name": "Google",
          "url": "https://google.com",
          "expected_return_code": 200,
          "assert_regex": "google"
        },
    """
    # Do request and measure time
    start_time = time.time()
    response = None
    try:
        response = requests.get(site['url'], timeout=10)
    except BaseException as exception:
        logging.debug(exception, exc_info=True)
        logging.error("Error happened! {}".format(exception))
    duration = time.time() - start_time

    # Collect data for kafka
    data = {
        'url': site['url'],
        'expected_return_code': site.get('expected_return_code'),
        'start_time': start_time,
        'duration': duration * 1000,  # Using milliseconds as unit
    }
    if response is None:
        data['return_code'] = 0
        data['content_length'] = 0
        data['content_check'] = 0
    else:
        data['return_code'] = response.status_code
        data['content_length'] = len(response.text)
        data['content_check'] = regex_search(site.get('assert_regex', None), response.text)

    logger.debug('data: %s', data)
    send_to_kafka(data)

    assert response is not None, 'Error happened in connection. Check logs for more information!'
    assert data['expected_return_code'] == data['return_code'], \
        'Fail: {} return code expected but it was {}'.format(site.get('expected_return_code'), response.status_code)
    assert data['content_check'], \
        'Fail: Cannot find anything with regular expression search "{}"'.format(site['assert_regex'])
