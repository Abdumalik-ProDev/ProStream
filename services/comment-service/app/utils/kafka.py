import json, logging
from aiokafka import AIOKafkaProducer
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)
_producer: Optional[AIOKafkaProducer] = None

async def get_producer(loop) -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        if not settings.KAFKA_BOOTSTRAP_SERVERS:
            raise ValueError("KAFKA_BOOTSTRAP_SERVERS is not set")
        _producer = AIOKafkaProducer(
            loop=loop,
            bootstrap_servers=[s.strip() for s in settings.KAFKA_BOOTSTRAP_SERVERS.split(",")],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await _producer.start()
    return _producer

async def publish_event(loop, topic: str, event_type: str, payload: dict):
    prod = await get_producer(loop)
    if not prod:
        logger.error("Kafka producer is not initialized")
        return
    message = json.dumps({
        "event": event_type,
        "payload": payload
    }).encode("utf-8")
    try:
        await prod.send_and_wait(topic, message)
        logger.info(f"Published event to {topic}: {event_type}")
    except Exception as e:
        logger.error(f"Failed to publish event to {topic}: {e}")