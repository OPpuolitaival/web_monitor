import requests
import pytest
import time
import logging
import json
import os

from kafka import KafkaProducer

logger = logging.getLogger(__name__)

# Read sites configuration from file
sites = list()
if not os.path.isfile('sites.json'):
    raise Exception('sites.json is expected to locate in current working directory!')
with open('sites.json') as f:
    sites = json.load(f)


@pytest.fixture(scope='session')
def kafka_json_sender():
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


@pytest.mark.parametrize('site', sites, ids=[x['name'] for x in sites])
def test_web_site(site, kafka_json_sender):
    # Do request and measure time
    start_time = time.time()
    r = requests.get(site['url'])
    duration = time.time() - start_time

    # Collect data for kafka
    data = {
        'expected_status_code': site.get('expected_status_code'),
        'status_code': r.status_code,
        'duration_ms': duration * 1000,
    }
    logger.debug('data: {}'.format(data))
    kafka_json_sender.send(data)

    assert site.get('expected_status_code') == r.status_code
    if 'assert_text' in list(site):
        assert site['assert_text'] in r.text
