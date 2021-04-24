"""
Process that reads messages from Kafka and send those to the postgresql
"""
import json
import logging
import sys
from time import sleep

import click
import psycopg2
from kafka import KafkaConsumer

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


class PostgreSqlConnector:

    def __init__(self, database_name, table_name, host, port, user, password):
        """

        :param database_name:
        :param table_name:
        :param host:
        :param port:
        :param user:
        :param password:
        """
        self.table_name = table_name
        self.conn = psycopg2.connect(host=host, port=port, dbname=database_name, user=user, password=password)

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
@click.option('--config', help='Configuration file')
@click.option('--verbose', default=False, is_flag=True, help='More verbose logging')
def start_process(config, verbose):
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    with open(config) as config_file:
        configuration = json.load(config_file)

    log.debug('Checking configuration..')
    assert 'kafka' in list(configuration)
    assert 'channel' in list(configuration['kafka'])
    assert 'bootstrap_servers' in list(configuration['kafka'])

    assert 'postgres' in list(configuration)
    postgres_config = configuration['postgres']
    for field in ['database_name', 'table_name', 'host', 'port']:
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
                value_deserializer=lambda message: json.loads(message))
            postgres_connector = PostgreSqlConnector(
                database_name=postgres_config['database_name'],
                table_name=postgres_config['table_name'],
                host=postgres_config['host'],
                port=postgres_config['port'],
                user=postgres_config.get('user', None),
                password=postgres_config.get('password', None)
            )

            log.debug("Waiting for messages..")
            for msg in kafka_consumer:
                log.debug('<= {}'.format(msg.value))
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
