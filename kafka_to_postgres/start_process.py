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

    def __init__(self, monitor_name='web_monitor'):
        self.measurements_table_name = monitor_name
        self.urls_table_name = '{}_urls'.format(monitor_name)
        # user='postgres' password='secret'
        self.conn = psycopg2.connect("host='localhost' port='5432' dbname='mydb'")

        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS {measurements_table_name} (
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
        CREATE INDEX IF NOT EXISTS measurement_ur ON {measurements_table_name} (url, return_code);        
        """.format(
            measurements_table_name=self.measurements_table_name,
            urls_table_name=self.urls_table_name
        ))
        # Make sure that table exists
        self.conn.commit()

    def insert_record(self, url, return_code, expected_return_code, duration, content_length, start_time,
                      content_check):
        cur = self.conn.cursor()
        cur.execute("""            
            INSERT INTO {measurements_table_name} (url, return_code, expected_return_code, duration, content_length, 
            start_time, content_check)
                    VALUES ('{url}', {return_code}, {expected_return_code}, {duration}, {content_length}, {start_time}, 
                    {content_check});""".format(
            urls_table_name=self.urls_table_name,
            measurements_table_name=self.measurements_table_name,
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
    assert 'postgres' in list(configuration)
    assert 'channel' in list(configuration['kafka'])
    assert 'bootstrap_servers' in list(configuration['kafka'])
    assert 'table_name' in list(configuration['postgres'])
    log.debug('Configuration OK')

    log.info("Starting process..")
    while True:
        log.debug("Loop..")
        sleep(0.1)  # Avoid busy loop
        try:
            consumer = KafkaConsumer(
                configuration['kafka']['channel'],
                bootstrap_servers=configuration['kafka']['bootstrap_servers'],
                value_deserializer=lambda message: json.loads(message))
            postgres_connector = PostgreSqlConnector(configuration['postgres']['table_name'])

            for msg in consumer:
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

        except KeyboardInterrupt:
            log.info("Stopping process..")
            sys.exit(1)
        except BaseException as exception:
            log.debug(exception, exc_info=True)


if __name__ == '__main__':
    log.info("Starts")
    start_process()
