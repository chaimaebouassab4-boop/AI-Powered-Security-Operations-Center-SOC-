import pytest
import time
import json
from kafka import KafkaConsumer
from agents.common.kafka_utils import KafkaHandler

class TestFullPipeline:
    """Tests du pipeline complet"""
    
    @pytest.fixture
    def kafka(self):
        return KafkaHandler("localhost:9093")
    
    def test_event_flows_through_pipeline(self, kafka):
        """Vérifie qu'un événement traverse tout le pipeline"""
        
        # 1. Injecter un événement dans events_raw
        test_event = {
            'event_id': 'test_001',
            'timestamp': '2025-01-15T10:00:00',
            'message': 'Failed password for admin from 192.168.1.100',
            'log_type': 'ssh'
        }
        
        kafka.send('events_raw', test_event, key='test_001')
        print("✅ Événement injecté dans events_raw")
        
        # 2. Attendre que les agents le traitent
        time.sleep(30)
        
        # 3. Vérifier qu'il arrive à events_final
        consumer = KafkaConsumer(
            'events_final',
            bootstrap_servers='localhost:9093',
            auto_offset_reset='earliest',
            consumer_timeout_ms=10000,
            value_deserializer=lambda m: json.loads(m.decode())
        )
        
        found = False
        for message in consumer:
            event = message.value
            if event.get('event_id') == 'test_001':
                found = True
                
                # Vérifications
                assert 'features' in event
                assert 'anomaly_score' in event
                assert 'llm_analysis' in event
                assert 'calibrated_confidence' in event
                assert 'mitre_techniques' in event
                assert 'action_taken' in event
                
                print(f"✅ Événement trouvé dans events_final")
                print(f"   Anomaly Score: {event['anomaly_score']}")
                print(f"   Threat Level: {event.get('threat_level')}")
                print(f"   Action: {event['action_taken']}")
                break
        
        consumer.close()
        assert found, "L'événement n'a pas atteint events_final"
    
    def test_latency_is_acceptable(self, kafka):
        """Vérifie que la latence est acceptable (<60s)"""
        start_time = time.time()
        
        test_event = {
            'event_id': f'latency_test_{start_time}',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'message': 'Test latency'
        }
        
        kafka.send('events_raw', test_event)
        
        consumer = KafkaConsumer(
            'events_final',
            bootstrap_servers='localhost:9093',
            auto_offset_reset='latest',
            consumer_timeout_ms=60000,
            value_deserializer=lambda m: json.loads(m.decode())
        )
        
        for message in consumer:
            if message.value.get('event_id') == test_event['event_id']:
                latency = time.time() - start_time
                print(f"⏱️  Latence: {latency:.2f} secondes")
                
                assert latency < 60, f"Latence trop élevée: {latency}s"
                consumer.close()
                return
        
        pytest.fail("Événement non reçu dans le temps imparti")
