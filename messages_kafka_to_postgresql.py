import json

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'web_tests',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda message: json.loads(message))

for msg in consumer:
    print(msg.value)
