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
def kafka_producer(test_config):
    """ Kafka producer as fixture for easy sending data to kafka from test cases """
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    topic = 'my_channel'

    def send(json_message):
        logger.debug("Sending kafka: topic: %s message: %s", topic, json_message)
        producer.send(topic, json_message)

    yield send
    producer.close()


@pytest.mark.web_page_monitring
def test_get_url(site):
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
    # kafka_json_sender.send(data)

    assert site.get('expected_status_code') == response.status_code
    if 'assert_text' in list(site):
        assert site['assert_text'] in response.text
