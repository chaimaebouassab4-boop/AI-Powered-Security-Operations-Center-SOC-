import yaml
from pathlib import Path
import sys
import math

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler

class TrustAgent:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)
        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("analyzed", "events_analyzed")
        self.output_topic = topics.get("calibrated", "events_calibrated")

        # Temperature scaling simple
        self.temperature = 1.5
        if "trust_agent" in self.cfg:
            self.temperature = float(self.cfg["trust_agent"].get("temperature", self.temperature))

    def calibrate(self, ev: dict) -> dict:
        conf = float((ev.get("analysis") or {}).get("confidence", 0.5))
        # Temperature scaling on logit
        eps = 1e-6
        conf = min(1-eps, max(eps, conf))
        logit = math.log(conf/(1-conf))
        scaled = 1/(1+math.exp(-logit/self.temperature))
        ev["analysis"]["calibrated_confidence"] = float(scaled)
        ev["stage"] = "calibrated"
        return ev

    def run(self):
        print(f"🎯 Trust : {self.input_topic} -> {self.output_topic} (T={self.temperature})")
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=self.calibrate,
            output_topic=self.output_topic,
            group_id="soc-trust",
        )

if __name__ == "__main__":
    TrustAgent().run()
