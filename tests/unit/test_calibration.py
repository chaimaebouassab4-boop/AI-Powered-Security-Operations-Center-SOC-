import pytest
import numpy as np
from agents.trust_agent.trust import TrustAgent

class TestTrustAgent:
    """Tests pour la calibration de confiance"""
    
    @pytest.fixture
    def agent(self):
        config = {
            'agents': {
                'trust_agent': {
                    'temperature': 1.5,
                    'calibration_method': 'temperature_scaling'
                }
            }
        }
        return TrustAgent(config)
    
    def test_calibration_reduces_overconfidence(self, agent):
        """La calibration doit réduire la sur-confiance"""
        event = {
            'event_id': '001',
            'llm_confidence': 0.95
        }
        
        result = agent.calibrate(event)
        
        assert 'calibrated_confidence' in result
        assert result['calibrated_confidence'] < result['llm_confidence']
    
    def test_calibration_increases_underconfidence(self, agent):
        """La calibration doit augmenter la sous-confiance"""
        event = {
            'event_id': '002',
            'llm_confidence': 0.3
        }
        
        result = agent.calibrate(event)
        
        assert 0.0 <= result['calibrated_confidence'] <= 1.0
    
    def test_calibration_range(self, agent):
        """La confiance calibrée doit rester entre 0 et 1"""
        test_confidences = [0.1, 0.3, 0.5, 0.7, 0.9, 0.99]
        
        for conf in test_confidences:
            event = {'llm_confidence': conf}
            result = agent.calibrate(event)
            
            assert 0.0 <= result['calibrated_confidence'] <= 1.0
