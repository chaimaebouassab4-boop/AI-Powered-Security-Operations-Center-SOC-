import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler
from features.feature_extractor import extract_features

class FeaturesAgent:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)

        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("collected", "events_collected")
        self.output_topic = topics.get("features", "events_with_features")

    def process(self, event: dict) -> dict:
        feats = extract_features(event)
        event["features"] = feats
        event["stage"] = "features"
        return event

    def run(self):
        print(f"🧩 Features actif : {self.input_topic} -> {self.output_topic}")
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=self.process,
            output_topic=self.output_topic,
            group_id="soc-features",
        )

if __name__ == "__main__":
    FeaturesAgent().run()
