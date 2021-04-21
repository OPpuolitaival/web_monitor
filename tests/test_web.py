# pylint: disable=redefined-outer-name
"""
Tests for web site monitoring
"""

import json
import logging
import time

import pytest
import requests
from kafka import KafkaProducer

logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def test_config(request):
    """ Fixture to read test configuration given by --config parameter in commandline"""
    with open(request.config.getoption('config')) as config_file:
        return json.load(config_file)


@pytest.fixture(scope='session')
def send_to_kafka(test_config):
    """ Kafka producer as fixture for easy sending data to kafka from test cases """
    producer = None
    if 'kafka' in test_config:
        producer = KafkaProducer(
            bootstrap_servers=test_config['kafka']['bootstrap_servers'],
            value_serializer=lambda message: json.dumps(message).encode('utf-8')
        )
        # Use web_tests as default channel if not configured
        topic = test_config['kafka'].get('channel', 'web_tests')

    def send(json_message):
        if producer is not None:
            logger.debug("Sending kafka: topic: %s message: %s", topic, json_message)
            producer.send(topic, json_message)

    yield send
    if producer is not None:
        producer.close()


@pytest.mark.web_page_monitring
def test_get_url(site, send_to_kafka):
    """ Executes HTTP get method for given site
        Example of site dict:
        {
            "name": "google",
            "url": "https://google.com",
            "expected_status_code": 200,
            "assert_text": "google"
        }
    """
    # Do request and measure time
    start_time = time.time()
    response = requests.get(site['url'])
    duration = time.time() - start_time

    # Collect data for kafka
    data = {
        'expected_status_code': site.get('expected_status_code'),
        'status_code': response.status_code,
        'duration_ms': duration * 1000,
        'expected_return_code': site.get('expected_status_code') == response.status_code,
        'content_length': len(response.text)  # Sometimes this helps to see that things changes
    }
    logger.debug('data: %s', data)
    send_to_kafka(data)

    assert site.get('expected_status_code') == response.status_code
    if 'assert_text' in list(site):
        assert site['assert_text'] in response.text
