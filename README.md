
# Web site monitoring project

This project is doing simple web page monitoring. It runs tests with pytest and send data to kafka. 
Then there is separated process to deliver messages from Kafka to postgresql for future usage. 

Main content:
1. [pytests](./pytests) folder contains tests which monitors web pages based on configuration
2. [monitor_job.groovy](./jenkins/monitor_job.groovy) for running tests in jenkins periodically
3. [start_process.py](./kafka_to_postgres/start_process.py) for delivering data from kafka to postgres



Run tests with example configuration:
```
cd pytests 
pytest --config ../config_example.json .
```

## Dockerization

With docker it is easier run or deliver executable container. 
This is needed to minimize network traffic and improve reliability in production environments. 

Build
```
docker build -t web_monitor:latest .
```

Run example test configuration:
```
docker run --rm -ti -v `pwd`:/config -w /web_monitor/pytests/ web_monitor bash -c "pytest --config /config/config_example.json ."
```

Start process which delives kafka messages to postgres 
```
docker run --rm -ti -v `pwd`:/config web_monitor bash -c "python3 kafka_to_postgres/start_process.py --config /config/config_remote.json"
```

## Developing tests

Check code formatting by running
```
pylint *
```