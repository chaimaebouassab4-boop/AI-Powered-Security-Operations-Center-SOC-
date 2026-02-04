import yaml
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler

class Collector:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)

        self.kafka = KafkaHandler(self.cfg["kafka"]["bootstrap_servers"])
        topics = self.cfg["kafka"]["topics"]
        self.input_topic = topics.get("raw", "events_raw")
        self.output_topic = topics.get("collected", "events_collected")

    def normalize(self, event: dict) -> dict:
        # Normalisation simple (tu peux enrichir plus tard)
        # S'assure que certains champs existent
        event.setdefault("stage", "collected")
        return event

    def run(self):
        def callback(ev):
            return self.normalize(ev)

        # Consomme input_topic et republie vers output_topic
        self.kafka.consume_and_process(
            input_topic=self.input_topic,
            callback=callback,
            output_topic=self.output_topic,
            group_id="soc-collector",
        )

if __name__ == "__main__":
    print("📡 Collector actif : events_raw -> events_collected")
    Collector().run()
