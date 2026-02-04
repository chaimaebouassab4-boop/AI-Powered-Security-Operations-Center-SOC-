import yaml, hashlib, time
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from common.kafka_utils import KafkaHandler


class LogTailer:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)

        self.bootstrap = self.cfg["kafka"]["bootstrap_servers"]
        self.topic_raw = self.cfg["kafka"]["topics"].get("raw", "events_raw")

        self.kafka = KafkaHandler(self.bootstrap)

    def tail_logs(self, log_path="/var/log/apache2/access.log"):
        # Lecture en mode "tail -f"
        with open(log_path, "r") as f:
            f.seek(0, 2)  # aller à la fin du fichier
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.2)
                    continue

                line = line.strip()
                if not line:
                    continue

                event = {
                    "event_id": hashlib.md5(line.encode()).hexdigest()[:16],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": line,
                    "log_type": "apache",   # ✅ IMPORTANT
                    "source": "apache_access",
                }

                # envoi vers le topic défini dans la config
                self.kafka.send(self.topic_raw, event, key=event["event_id"])
                print(f"📤 {event['event_id']}")


if __name__ == "__main__":
    LogTailer("config/config.yaml").tail_logs()
