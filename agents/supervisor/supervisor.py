import time
import json
from kafka import KafkaConsumer

def run_supervisor():
    print("📊 Supervisor actif : Surveillance du pipeline SOC...")
    consumer = KafkaConsumer(
        'decisions',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    for message in consumer:
        event = message.value
        print(f"📈 Event {event.get('event_id')} traité - Status: OK")

if __name__ == "__main__":
    run_supervisor()
