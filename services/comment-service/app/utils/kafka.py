import logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)

producer: AIOKafkaProducer | None = None


async def init_kafka():
    """Initialize Kafka producer."""
    global producer
    if producer is None:
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers
            )
            await producer.start()
            logger.info("✅ Kafka producer connected to %s", settings.kafka_bootstrap_servers)
        except Exception as e:
            logger.error("❌ Failed to connect Kafka: %s", e)
            raise


async def close_kafka():
    """Close Kafka producer."""
    global producer
    if producer:
        await producer.stop()
        logger.info("🛑 Kafka producer stopped")
        producer = None


async def send_event(topic: str, key: str, value: dict):
    """Send an event to Kafka."""
    global producer
    if producer is None:
        raise RuntimeError("Kafka producer not initialized")

    try:
        await producer.send_and_wait(
            topic,
            key=key.encode("utf-8"),
            value=str(value).encode("utf-8")
        )
        logger.info("📤 Sent event to Kafka topic=%s key=%s", topic, key)
    except Exception as e:
        logger.error("❌ Failed to send Kafka event: %s", e)
        raise