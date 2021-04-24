# pylint: disable=redefined-outer-name
"""
Pytest fixtures
"""
import json
import logging

import pytest
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
            security_protocol=test_config['kafka'].get('security_protocol', 'PLAINTEXT'),
            ssl_cafile=test_config['kafka'].get('ca_path', None),
            ssl_certfile=test_config['kafka'].get('cert_path', None),
            ssl_keyfile=test_config['kafka'].get('key_path', None),
            value_serializer=lambda message: json.dumps(message).encode('utf-8'),
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
