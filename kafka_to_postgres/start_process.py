# pylint: disable=no-value-for-parameter,broad-except,unnecessary-lambda
"""
Process that reads messages from Kafka and send those to the postgresql
"""
import json
import logging
import os.path
import sys
from time import sleep

import click
import psycopg2
from kafka import KafkaConsumer

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


class PostgreSqlConnector:
    """ Helps Postgres connection handling """

    def __init__(self, table_name, uri):
        """
        :param table_name: Table name which will be create if not exists yet
        :param uri: database uri containing secrets and database name
        """
        self.table_name = table_name
        self.conn = psycopg2.connect(uri)

        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS {table_name} (
              id                      SERIAL NOT NULL PRIMARY KEY,
              created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              url                     varchar(255) NOT NULL,
              return_code             smallint,
              expected_return_code    smallint,
              duration                float(20),
              content_length          integer,
              start_time              float(20),
              content_check           boolean
        );
        CREATE INDEX IF NOT EXISTS measurement_ur ON {table_name} (url, return_code);        
        """.format(table_name=self.table_name))
        # Make sure that table exists
        self.conn.commit()

    def insert_record(self, url, return_code, expected_return_code, duration, content_length, start_time,
                      content_check):
        """ Add new record to the database """
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO {table_name} (url, return_code, expected_return_code, duration, content_length, 
            start_time, content_check)
                    VALUES ('{url}', {return_code}, {expected_return_code}, {duration}, {content_length}, {start_time}, 
                    {content_check});""".format(
            table_name=self.table_name,
            url=url,
            return_code=return_code,
            expected_return_code=expected_return_code,
            duration=duration,
            content_length=content_length,
            start_time=start_time,
            content_check=content_check))
        # Make sure that record is committed
        self.conn.commit()


@click.command()
@click.option('--config', help='Configuration file', required=True)
@click.option('--verbose', default=False, is_flag=True, help='More verbose logging')
def start_process(config, verbose):
    """ Process staring method """

    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if not os.path.isfile(config):
        raise Exception('{} does not exits!'.format(config))

    with open(config) as config_file:
        configuration = json.load(config_file)

    log.debug('Checking configuration..')
    assert 'kafka' in list(configuration)
    assert 'channel' in list(configuration['kafka'])
    assert 'bootstrap_servers' in list(configuration['kafka'])

    assert 'postgres' in list(configuration)
    postgres_config = configuration['postgres']
    for field in ['database_name', 'table_name', 'uri']:
        assert field in list(postgres_config)
    log.debug('Configuration OK')

    log.info("Starting process..")
    while True:
        log.debug("Loop..")
        sleep(0.1)  # Avoid busy loop
        try:
            kafka_consumer = KafkaConsumer(
                configuration['kafka']['channel'],
                bootstrap_servers=configuration['kafka']['bootstrap_servers'],
                security_protocol=configuration['kafka'].get('security_protocol', 'PLAINTEXT'),
                ssl_cafile=configuration['kafka'].get('ca_path', None),
                ssl_certfile=configuration['kafka'].get('cert_path', None),
                ssl_keyfile=configuration['kafka'].get('key_path', None),
                value_deserializer=lambda message: json.loads(message))
            postgres_connector = PostgreSqlConnector(
                table_name=postgres_config['table_name'],
                uri=postgres_config['uri'],
            )

            log.debug("Waiting for messages..")
            for msg in kafka_consumer:
                log.info('<= {}'.format(msg.value))
                postgres_connector.insert_record(
                    url=msg.value['url'],
                    return_code=msg.value['return_code'],
                    expected_return_code=msg.value['expected_return_code'],
                    duration=msg.value['duration'],
                    content_length=msg.value['content_length'],
                    start_time=msg.value['start_time'],
                    content_check=msg.value['content_check']
                )
                log.debug('Message send to postgres')

        except KeyboardInterrupt:
            log.info("Stopping process..")
            sys.exit(0)
        except BaseException as exception:
            log.error(exception, exc_info=True)


if __name__ == '__main__':
    start_process()
