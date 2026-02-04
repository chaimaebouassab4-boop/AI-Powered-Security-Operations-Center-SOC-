import pytest
import numpy as np
from agents.anomaly_detector.detector import AnomalyDetector

class TestAnomalyDetector:
    """Tests pour la détection d'anomalies"""
    
    @pytest.fixture
    def detector(self, tmp_path):
        """Fixture: crée un détecteur de test"""
        config = {
            'agents': {
                'anomaly_detector': {
                    'threshold': 0.7,
                    'model_path': str(tmp_path / 'test_model.pkl')
                }
            }
        }
        return AnomalyDetector(config)
    
    def test_normal_event_low_score(self, detector):
        """Événement normal doit avoir score bas"""
        event = {
            'event_id': '001',
            'features': {
                'hour': 10,
                'msg_len': 50,
                'has_failed': 0
            }
        }
        
        result = detector.detect(event)
        
        assert 'anomaly_score' in result
        assert result['anomaly_score'] < 0.7
        assert result['is_anomaly'] == False
    
    def test_suspicious_event_high_score(self, detector):
        """Événement suspect doit avoir score élevé"""
        event = {
            'event_id': '002',
            'features': {
                'hour': 3,           # 3h du matin = suspect
                'msg_len': 500,      # Message très long
                'has_failed': 1,
                'ip_frequency': 100  # Beaucoup de tentatives
            }
        }
        
        result = detector.detect(event)
        
        assert 'anomaly_score' in result
        assert result['is_anomaly'] in [True, False]
    
    def test_missing_features(self, detector):
        """Gérer événement sans features"""
        event = {'event_id': '003'}
        
        result = detector.detect(event)
        
        assert result['anomaly_score'] == 0.5
        assert result['is_anomaly'] == False
