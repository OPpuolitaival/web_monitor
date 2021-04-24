
# Web site monitoring project

This project enable web site monitoring


Run tests with example configuration:
```
cd pytests 
pytest --config ../config_example.json .
```

## Using Docker

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