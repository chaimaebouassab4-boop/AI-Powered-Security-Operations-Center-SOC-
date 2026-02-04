import pytest
from agents.common.kafka_utils import KafkaHandler

class TestKafkaHandler:
    def test_kafka_initialization(self):
        """Vérifie l'initialisation à vide du producteur"""
        kafka = KafkaHandler("localhost:9093")
        assert kafka.servers == "localhost:9093"
        assert kafka.producer is None

    def test_send_message(self, mocker):
        """Vérifie la logique d'envoi via un mock de Kafka"""
        # On patche le KafkaProducer DIRECTEMENT dans le module qui l'utilise
        mock_producer_class = mocker.patch('agents.common.kafka_utils.KafkaProducer')
        mock_producer_instance = mock_producer_class.return_value
        
        # On simule le comportement du futur de Kafka
        mock_future = mocker.MagicMock()
        mock_producer_instance.send.return_value = mock_future
        
        kafka = KafkaHandler("localhost:9093")
        test_event = {'event_id': '123', 'message': 'Test'}
        
        # Exécution
        result = kafka.send('test_topic', test_event, key='123')
        
        # Assertions
        assert result is True
        # On vérifie que la méthode send de l'instance a été appelée
        mock_producer_instance.send.assert_called_once()
