import pytest
from agents.common.kafka_utils import KafkaHandler

def test_kafka_handler():
    kafka = KafkaHandler("localhost:9093")
    assert kafka.servers == "localhost:9093"

def test_feature_extraction():
    from agents.features.extractor import extract_features
    event = {
        'message': 'Failed password',
        'timestamp': '2025-01-01T00:00:00'
    }
    result = extract_features(event)
    assert 'features' in result
    assert result['features']['has_failed'] == 1
