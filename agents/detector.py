import numpy as np
import pickle
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Any, Optional


class AnomalyDetector:
    """Agent de détection d'anomalies utilisant Isolation Forest"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le détecteur d'anomalies
        Args:
            config: Configuration contenant threshold et model_path
        """
        self.config = config.get('agents', {}).get('anomaly_detector', {})
        self.threshold = self.config.get('threshold', 0.7)
        self.model_path = self.config.get('model_path', 'models/anomaly_model.pkl')
        
        # Initialiser le modèle
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Features utilisées
        self.feature_names = [
            'bytes_sent', 'bytes_received', 'duration', 
            'port', 'hour', 'day_of_week', 'is_tor'
        ]
        
        # TOR exit nodes (exemple limité)
        self.known_tor_exits = {
            '185.220.101.1', '185.220.101.2', '185.220.101.3',
            '185.220.102.1', '185.220.102.2', '185.220.102.3'
        }
    
    def extract_features(self, event: Dict[str, Any]) -> np.ndarray:
        """
        Extrait les features numériques d'un événement
        Args:
            event: Événement à analyser
        Returns:
            Array numpy des features
        """
        features = []
        
        # Features numériques de base
        features.append(event.get('bytes_sent', 0))
        features.append(event.get('bytes_received', 0))
        features.append(event.get('duration', 0))
        features.append(event.get('port', 0))
        
        # Features temporelles
        time_features = self.extract_time_features(event)
        features.append(time_features.get('hour', 12))
        features.append(time_features.get('day_of_week', 0))
        
        # Feature de réputation IP
        dest_ip = event.get('destination_ip', '')
        is_tor = 1 if dest_ip in self.known_tor_exits else 0
        features.append(is_tor)
        
        return np.array(features).reshape(1, -1)
    
    def extract_time_features(self, event: Dict[str, Any]) -> Dict[str, int]:
        """
        Extrait les features temporelles d'un événement
        Args:
            event: Événement contenant un timestamp
        Returns:
            Dict avec hour et day_of_week
        """
        timestamp = event.get('timestamp')
        if timestamp is None:
            return {'hour': 12, 'day_of_week': 0}
        
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
        else:
            dt = timestamp
        
        return {
            'hour': dt.hour,
            'day_of_week': dt.weekday()
        }
    
    def check_ip_reputation(self, ip: str) -> str:
        """
        Vérifie la réputation d'une IP
        Args:
            ip: Adresse IP à vérifier
        Returns:
            'clean', 'suspicious', ou 'malicious'
        """
        # IP privées sont considérées comme clean
        if ip.startswith(('192.168.', '10.', '172.')):
            return 'clean'
        
        # TOR exit nodes
        if ip in self.known_tor_exits:
            return 'suspicious'
        
        return 'unknown'
    
    def analyze_event(self, event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse un événement pour détecter des anomalies
        Args:
            event: Événement à analyser
        Returns:
            Dict contenant le score et les métadonnées
        """
        if event is None:
            return {
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'confidence': 0.0,
                'error': 'Event is None'
            }
        
        try:
            # Extraire les features
            features = self.extract_features(event)
            
            # Calculer le score d'anomalie
            score = self.model.decision_function(features)[0]
            
            # Normaliser le score entre 0 et 1
            normalized_score = self._normalize_score(score)
            
            # Déterminer si c'est une anomalie
            is_anomaly = normalized_score > self.threshold
            
            result = {
                'is_anomaly': is_anomaly,
                'anomaly_score': float(normalized_score),
                'confidence': float(abs(normalized_score - self.threshold)),
                'features': features.tolist()[0]
            }
            
            # Ajouter les raisons si anomalie détectée
            if is_anomaly:
                result['reasons'] = self._generate_reasons(event, features)
            
            return result
            
        except Exception as e:
            return {
                'is_anomaly': False,
                'anomaly_score': 0.5,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def detect(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detects anomalies in an event (alias for analyze_event)
        
        Args:
            event: Event to analyze
            
        Returns:
            Dict containing detection results
        """
        return self.analyze_event(event)
    
    def _normalize_score(self, score: float) -> float:
        """
        Normalise le score d'Isolation Forest entre 0 et 1
        Args:
            score: Score brut du modèle
        Returns:
            Score normalisé entre 0 et 1
        """
        # Isolation Forest retourne des scores négatifs pour les anomalies
        # On inverse et normalise
        return float(1 / (1 + np.exp(-score)))
    
    def _generate_reasons(self, event: Dict[str, Any], features: np.ndarray) -> List[str]:
        """
        Génère les raisons pour lesquelles un événement est considéré comme anomalie
        Args:
            event: Événement analysé
            features: Features extraites
        Returns:
            Liste de raisons descriptives
        """
        reasons = []
        
        # Vérifier les transferts de données suspects
        bytes_sent = event.get('bytes_sent', 0)
        bytes_received = event.get('bytes_received', 0)
        
        if bytes_sent > 10000000:  # Plus de 10MB
            reasons.append(f"Volume de données envoyé élevé: {bytes_sent / 1000000:.2f} MB")
        
        if bytes_received > 50000000:  # Plus de 50MB
            reasons.append(f"Volume de données reçu élevé: {bytes_received / 1000000:.2f} MB")
        
        # Vérifier la durée de connexion
        duration = event.get('duration', 0)
        if duration > 3600:  # Plus d'une heure
            reasons.append(f"Connexion très longue: {duration / 3600:.2f} heures")
        
        # Vérifier le port
        port = event.get('port', 0)
        suspicious_ports = {22, 23, 3389, 445, 139}
        if port in suspicious_ports:
            reasons.append(f"Port suspect: {port}")
        
        # Vérifier l'heure
        time_features = self.extract_time_features(event)
        hour = time_features.get('hour', 12)
        if hour < 6 or hour > 22:
            reasons.append(f"Activité en dehors des heures normales: {hour}h")
        
        # Vérifier la réputation IP
        dest_ip = event.get('destination_ip', '')
        reputation = self.check_ip_reputation(dest_ip)
        if reputation == 'suspicious':
            reasons.append(f"Connexion vers IP suspecte: {dest_ip}")
        elif reputation == 'malicious':
            reasons.append(f"Connexion vers IP malveillante: {dest_ip}")
        
        return reasons
    
    def analyze_batch(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyse un batch d'événements
        Args:
            events: Liste d'événements à analyser
        Returns:
            Liste de résultats d'analyse
        """
        results = []
        for event in events:
            result = self.analyze_event(event)
            results.append(result)
        return results
    
    def train(self, training_data: List[Dict[str, Any]]) -> None:
        """
        Entraîne le modèle sur des données historiques
        Args:
            training_data: Liste d'événements pour l'entraînement
        """
        if not training_data:
            return
        
        # Extraire les features de tous les événements
        features_list = []
        for event in training_data:
            features = self.extract_features(event)
            features_list.append(features.flatten())
        
        X = np.array(features_list)
        
        # Entraîner le modèle
        self.model.fit(X)
    
    def save_model(self, path: str) -> None:
        """
        Sauvegarde le modèle entraîné
        Args:
            path: Chemin de sauvegarde
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
    
    def load_model(self, path: str) -> None:
        """
        Charge un modèle sauvegardé
        Args:
            path: Chemin du modèle
        """
        if Path(path).exists():
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            print(f"Model file not found: {path}")
