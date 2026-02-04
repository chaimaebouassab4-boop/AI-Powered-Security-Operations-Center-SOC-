import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler

class MitreMapper:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)
        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("anomaly", "events_with_anomaly")
        self.output_topic = topics.get("mitre", "events_with_mitre")

    def map_mitre(self, ev: dict) -> dict:
        msg = (ev.get("message") or "").lower()
        feats = ev.get("features") or {}
        is_http = int(feats.get("is_http", 0)) == 1
        is_error = int(feats.get("is_error", 0)) == 1

        technique = None
        tactic = None
        reason = []

        # Heuristiques simples pour ton scénario (fuzzing / énumération)
        if "gobuster" in msg or "dirb" in msg:
            technique = "T1595.001"  # Active Scanning: Scanning IP Blocks (approx)
            tactic = "Reconnaissance"
            reason.append("User-Agent gobuster/dirb détecté")
        elif is_http and is_error and ("doesnotexist" in msg or " 404 " in msg):
            technique = "T1595"      # Active Scanning (générique)
            tactic = "Reconnaissance"
            reason.append("Beaucoup de requêtes HTTP 404 -> énumération/fuzzing probable")

        ev["mitre"] = {
            "tactic": tactic,
            "technique_id": technique,
            "reason": reason
        }
        ev["stage"] = "mitre"
        return ev

    def run(self):
        print(f"🧠 MITRE mapper : {self.input_topic} -> {self.output_topic}")
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=self.map_mitre,
            output_topic=self.output_topic,
            group_id="soc-mitre",
        )

if __name__ == "__main__":
    MitreMapper().run()
