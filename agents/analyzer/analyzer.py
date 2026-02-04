import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler

class AnalyzerAgent:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)
        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("anomaly", "events_with_anomaly")
        self.output_topic = topics.get("analyzed", "events_analyzed")

    def analyze(self, ev: dict) -> dict:
        feats = ev.get("features") or {}
        is_http = int(feats.get("is_http", 0)) == 1
        is_error = int(feats.get("is_error", 0)) == 1
        anom = bool(ev.get("is_anomaly", False))
        score = float(ev.get("anomaly_score", 0.0))

        # Heuristique simple (acceptable pour rendu)
        if anom or (is_http and is_error):
            threat = "medium"
            conf = max(0.6, min(0.95, 0.6 + score))
        else:
            threat = "low"
            conf = 0.4

        ev["analysis"] = {
            "threat_level": threat,
            "confidence": float(conf),
            "summary": "HTTP enumeration / errors" if (is_http and is_error) else "Normal traffic"
        }
        ev["stage"] = "analyzed"
        return ev

    def run(self):
        print(f"🧠 Analyzer : {self.input_topic} -> {self.output_topic}")
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=self.analyze,
            output_topic=self.output_topic,
            group_id="soc-analyzer",
        )

if __name__ == "__main__":
    AnalyzerAgent().run()
