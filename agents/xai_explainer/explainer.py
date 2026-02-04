import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler

class Explainer:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)
        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("mitre", "events_with_mitre")
        self.output_topic = topics.get("explained", "events_explained")

    def explain(self, ev: dict) -> dict:
        feats = ev.get("features") or {}
        analysis = ev.get("analysis") or {}
        mitre = ev.get("mitre") or {}
        msg = ev.get("message", "")

        parts = []
        if feats.get("is_http") == 1 and feats.get("is_error") == 1:
            parts.append("Requêtes HTTP en erreur (>=400), typiques d’énumération/fuzzing.")
        if mitre.get("technique_id"):
            parts.append(f"Mapping MITRE : {mitre.get('technique_id')} ({mitre.get('tactic')}).")
        parts.append(f"Niveau: {analysis.get('threat_level')} | Confiance calibrée: {analysis.get('calibrated_confidence', analysis.get('confidence'))}")

        ev["xai_explanation"] = " ".join(parts)[:600]
        ev["stage"] = "explained"
        return ev

    def run(self):
        print(f"🧾 XAI : {self.input_topic} -> {self.output_topic}")
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=self.explain,
            output_topic=self.output_topic,
            group_id="soc-xai",
        )

if __name__ == "__main__":
    Explainer().run()
