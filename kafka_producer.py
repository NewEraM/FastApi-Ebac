from kafka import KafkaProducer
import json
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")

producer = None

def ger_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return producer

def enviar_evento(topico: str, evento: dict):
    prod = ger_producer()
    prod.send(topico, evento)
    prod.flush()
    