import requests
import pytest
import time
import logging
import json

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def test_config(request):
    with open(request.config.getoption('config')) as f:
        return json.load(f)


@pytest.fixture(scope='session')
def kafka_json_sender(test_config):
    # TODO: Read address from configuration
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    topic = 'my_channel'

    def send(json_message):
        logger.debug("Sending kafka: topic: {}, message: {}".format(topic, json_message))
        producer.send(topic, json_message)

    yield send
    producer.close()


@pytest.mark.web_page_monitring
def test_web_site(site, test_config):
    # Do request and measure time
    start_time = time.time()
    r = requests.get(site['url'])
    duration = time.time() - start_time

    # Collect data for kafka
    data = {
        'expected_status_code': site.get('expected_status_code'),
        'status_code': r.status_code,
        'duration_ms': duration * 1000,
        'expected_return_code': site.get('expected_status_code') == r.status_code,
        'content_length': len(r.text)  # Sometimes this helps to see that things changes
    }
    logger.debug('data: {}'.format(data))
    # kafka_json_sender.send(data)

    assert site.get('expected_status_code') == r.status_code
    if 'assert_text' in list(site):
        assert site['assert_text'] in r.text
