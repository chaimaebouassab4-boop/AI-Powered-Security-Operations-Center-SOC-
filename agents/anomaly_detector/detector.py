import yaml
import numpy as np
from pathlib import Path
import sys
from collections import deque
from sklearn.ensemble import IsolationForest

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler


class AnomalyDetectorAgent:
    """
    Consomme events_with_features et publie events_with_anomaly.
    Utilise IsolationForest sur les features disponibles :
    has_failed, msg_len, hour, is_http, is_error
    """

    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)

        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("features", "events_with_features")
        self.output_topic = topics.get("anomaly", "events_with_anomaly")

        # seuil : si présent dans cfg['analyzer']['threshold'] (ton YAML), sinon default
        self.threshold = 0.75
        if "analyzer" in self.cfg and isinstance(self.cfg["analyzer"], dict):
            self.threshold = float(self.cfg["analyzer"].get("threshold", self.threshold))

        # warmup : on entraîne après avoir vu N events
        self.warmup_n = 80
        self.buffer = deque(maxlen=300)
        self.model = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
        self.is_trained = False

    def _vectorize(self, ev: dict) -> np.ndarray:
        feats = ev.get("features") or {}
        return np.array([
            float(feats.get("has_failed", 0)),
            float(feats.get("msg_len", 0)),
            float(feats.get("hour", 0)),
            float(feats.get("is_http", 0)),
            float(feats.get("is_error", 0)),
        ], dtype=float)

    def _maybe_train(self):
        if self.is_trained:
            return
        if len(self.buffer) < self.warmup_n:
            return
        X = np.vstack(list(self.buffer))
        self.model.fit(X)
        self.is_trained = True
        print(f"✅ Anomaly model trained on {len(self.buffer)} events")

    def process(self, ev: dict) -> dict:
        x = self._vectorize(ev)
        self.buffer.append(x)
        self._maybe_train()

        # Tant que pas entraîné : score neutre
        if not self.is_trained:
            ev["anomaly_score"] = 0.0
            ev["is_anomaly"] = False
            ev["confidence"] = 0.0
            ev["stage"] = "anomaly"
            ev["note"] = f"warmup ({len(self.buffer)}/{self.warmup_n})"
            return ev

        # IsolationForest: decision_function > 0 normal, < 0 anomal
        score = float(self.model.decision_function([x])[0])
        # On convertit en "anomaly_score" où plus grand = plus suspect
        anomaly_score = float(-score)

        # règle simple : anomalie si http error (beaucoup de 404) OU score dépasse seuil
        feats = ev.get("features") or {}
        is_error = int(feats.get("is_error", 0)) == 1
        is_http = int(feats.get("is_http", 0)) == 1

        ev["anomaly_score"] = anomaly_score
        ev["is_anomaly"] = bool((anomaly_score >= self.threshold) or (is_http and is_error))
        ev["confidence"] = min(1.0, anomaly_score)  # simple bornage
        ev["stage"] = "anomaly"
        return ev

    def run(self):
        print(f"🚨 AnomalyDetector actif : {self.input_topic} -> {self.output_topic} (threshold={self.threshold})")
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=self.process,
            output_topic=self.output_topic,
            group_id="soc-anomaly",
        )


if __name__ == "__main__":
    AnomalyDetectorAgent().run()
