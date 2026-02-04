import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler

class Responder:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)
        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("explained", "events_explained")
        self.final_topic = topics.get("final", "events_final")
        self.alerts_topic = topics.get("alerts", "alerts")

    def decide(self, ev: dict) -> dict:
        analysis = ev.get("analysis") or {}
        mitre = ev.get("mitre") or {}
        feats = ev.get("features") or {}

        threat = analysis.get("threat_level", "low")
        conf = float(analysis.get("calibrated_confidence", analysis.get("confidence", 0.5)))

        action = "IGNORE"
        severity = "low"

        if mitre.get("technique_id") or (feats.get("is_http")==1 and feats.get("is_error")==1):
            action = "ALERT"
            severity = "medium"
        if threat in ("high",) or conf >= 0.75:
            action = "ALERT"
            severity = "high"

        ev["response"] = {"action": action, "severity": severity}
        ev["stage"] = "final"

        # Si ALERT => publier aussi dans alerts
        if action == "ALERT":
            alert = {
                "alert_id": ev.get("event_id"),
                "timestamp": ev.get("timestamp"),
                "severity": severity,
                "technique_id": (mitre or {}).get("technique_id"),
                "tactic": (mitre or {}).get("tactic"),
                "reason": (mitre or {}).get("reason"),
                "explanation": ev.get("xai_explanation"),
                "raw_event": ev,
            }
            self.kafka.send(self.alerts_topic, alert, key=str(alert["alert_id"]))

        return ev

    def run(self):
        print(f"🚨 Responder : {self.input_topic} -> {self.final_topic} (+alerts)")
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=self.decide,
            output_topic=self.final_topic,
            group_id="soc-responder",
        )

if __name__ == "__main__":
    Responder().run()
