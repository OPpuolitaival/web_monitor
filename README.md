
# Web site monitoring project

This project is doing simple web page monitoring. It runs tests with pytest and send data to kafka. 
Then there is separated process to deliver messages from Kafka to postgresql for future usage. 

Main content:
1. [pytests](./pytests) folder contains tests which monitors web pages based on configuration
2. [monitor_job.groovy](./jenkins/monitor_job.groovy) for running tests in jenkins periodically
3. [start_process.py](./kafka_to_postgres/start_process.py) for delivering data from kafka to postgres

## Requirements

* Kafka instance running
* PostgreSQL instance running

## Setup

1. Kafka
Setup Kafka locally with [this guidance](https://kafka.apache.org/quickstart) or setup remote instance for example using [aiven.io](https://aiven.io/) service
   
2. PostgreSQL
Setup local instance with [postgresql.org guide](https://www.postgresql.org/) or setup remote instance for example using [aiven.io](https://aiven.io/) service
* Create kafka channel

3. Python & requirements
Note: If you don't want to install python locally you can always use dockerized version
* Install python 3.6 or newer
* Run `pip3 install -r requirements.txt`

4. Create configuration

See configuration example files:
* [config/only_tests_example.json](config/only_tests_example.json) - Just running tests without data flow
* [config/local_config_example.json](config/local_config_example.json) - How to use local instances of Kafka / PostgreSQL
* [config/remote_config_example.json](config/remote_config_example.json) - How to use remote instances of Kafka / PostgreSQL

Configuration file documentation:
(This is not valid json. For copying purposes use some of example files)
```json
{
  "kafka": {
    "bootstrap_servers": "localhost:9092",  // <kafka bootstrap server url and port>
    "channel": "web_monitor", // Kafka channel name
    "security_protocol": "SSL", // Security protocol
    "ca_path": "/path/to/ca.pem", // CA certificate
    "cert_path": "/path/to/service.cert", // Access certificate
    "key_path": "/path/to/service.key" // Access key
  },
  "postgres": {
    "table_name": "web_monitor_measurements", // Used table name
    // Uri containing also authentication information and database name
    "uri": "postgres://avnadmin:<secret>.aivencloud.com:<port>/<database-name>?sslmode=require"
  },
  // List of sites which will be monitored
  "sites": [
    {
      "name": "Google", // Name just for test results
      "url": "https://google.com", // Url where to make HTTP GET
      "expected_return_code": 200, // Expected status code of response
      "assert_regex": "google" // Assert that regular expression search can find this
    }
  ]
}
```


## Run code

Run Kafka to PostgreSQL process:
```bash
python3 kafka_to_postgres/start_process.py --config config_example.json .
```

Run tests with example configuration:
```bash
cd pytests 
pytest --config ../config_example.json .
```

## Setup & running with docker

With docker it is easier run or deliver executable container. 
This is needed to minimize network traffic and improve reliability in production environments. 

Build
```bash
docker build -t web_monitor:latest .
```

Run example test configuration:
```bash
docker run --rm -ti -v `pwd`:/config -w /web_monitor/pytests/ web_monitor bash -c "pytest --config /config/config_example.json ."
```

Start process which delives kafka messages to postgres 
```bash
docker run --rm -ti -v `pwd`:/config web_monitor bash -c "python3 kafka_to_postgres/start_process.py --config /config/config_remote.json"
```

## Developing tests

Check code formatting by running
```bash
pylint *
```