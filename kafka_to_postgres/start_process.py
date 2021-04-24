import json
import logging
import sys
from time import sleep

import click
from kafka import KafkaConsumer

log = logging.getLogger(__name__)


@click.command()
@click.option('--config-file', help='Number of greetings.')
@click.option('--verbose', default=False, is_flag=True, help='More verbose logging')
def start_process(config_file, verbose):
    if verbose:
        log.setLevel(logging.DEBUG)

    while True:
        sleep(0.1)  # Avoid busy loop
        try:
            consumer = KafkaConsumer(
                'web_tests',
                bootstrap_servers='localhost:9092',
                value_deserializer=lambda message: json.loads(message))
            for msg in consumer:
                print(msg.value)

        except KeyboardInterrupt:
            print("Ok ok, quitting")
            sys.exit(1)
        except BaseException as exception:
            log.debug(exception, exc_info=True)
