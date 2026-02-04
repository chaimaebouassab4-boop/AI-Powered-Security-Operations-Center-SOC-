import pytest
from datetime import datetime
from agents.features.extractor import extract_features

class TestFeatureExtractor:
    """Tests pour l'extraction de features"""
    
    def test_extract_temporal_features(self):
        """Vérifie extraction des features temporelles"""
        event = {
            'event_id': '001',
            'timestamp': '2025-01-15T14:30:00',
            'message': 'Test event'
        }
        
        result = extract_features(event)
        
        assert 'features' in result
        assert 'hour' in result['features']
        assert result['features']['hour'] == 14
    
    def test_extract_ssh_failed_login(self):
        """Vérifie détection de tentative SSH échouée"""
        event = {
            'event_id': '002',
            'message': 'Failed password for admin from 192.168.1.100',
            'timestamp': '2025-01-15T10:00:00'
        }
        
        result = extract_features(event)
        
        assert result['features']['has_failed'] == 1
        assert result['features']['msg_len'] > 0
    
    def test_extract_http_features(self):
        """Vérifie extraction features HTTP"""
        event = {
            'event_id': '003',
            'message': 'GET /admin HTTP/1.1 404',
            'log_type': 'http',
            'status_code': 404
        }
        
        result = extract_features(event)
        
        assert result['features'].get('is_http') == 1
        assert result['features'].get('is_error') == 1
    
    def test_empty_event(self):
        """Vérifie que le code gère les événements vides"""
        event = {}
        result = extract_features(event)
        
        assert 'features' in result
        assert isinstance(result['features'], dict)
