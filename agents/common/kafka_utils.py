# agents/common/kafka_utils.py
from kafka import KafkaConsumer, KafkaProducer
import json
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class KafkaHandler:
    def __init__(self, bootstrap_servers: str):
        """Initialise la connexion Kafka pour le SOC."""
        self.bootstrap_servers = bootstrap_servers

        # Producer: sérialise en JSON utf-8
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=3,
        )

    def send(self, topic: str, value: Any, key: Optional[str] = None, timeout: int = 10) -> None:
        """Envoie un message au topic Kafka (option key)."""
        try:
            fut = self.producer.send(
                topic,
                value=value,
                key=key.encode("utf-8") if key else None
            )
            # Force l'erreur si Kafka refuse/timeout
            fut.get(timeout=timeout)
            self.producer.flush()
            logger.info("📤 Message envoyé au topic: %s", topic)
        except Exception as e:
            logger.exception("❌ Erreur d'envoi vers %s: %r", topic, e)
            raise

    def consume_and_process(
        self,
        input_topic: str,
        callback: Callable[[dict], Optional[dict]],
        output_topic: Optional[str] = None,
        group_id: str = "soc-group",
        auto_offset_reset: str = "earliest",
    ) -> None:
        """Consomme un topic, applique callback, et publie sur output_topic si fourni."""
        consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            group_id=group_id,
        )

        logger.info("📡 Écoute active sur: %s (group=%s)", input_topic, group_id)
        for message in consumer:
            try:
                result = callback(message.value)
                if result is not None and output_topic:
                    # event_id si existe → key Kafka
                    k = result.get("event_id") if isinstance(result, dict) else None
                    self.send(output_topic, result, key=k)
                    logger.info("✅ Événement transféré vers: %s", output_topic)
            except Exception as e:
                logger.exception("❌ Erreur traitement message: %r", e)
