import json
import logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)
_producer: AIOKafkaProducer | None = None

async def get_producer() -> AIOKafkaProducer | None:
    global _producer
    if _producer is None:
        servers = settings.KAFKA_BOOTSTRAP.split(",") if settings.KAFKA_BOOTSTRAP else []
        if not servers:
            return None
        _producer = AIOKafkaProducer(bootstrap_servers=servers)
        await _producer.start()
    return _producer

async def publish_event(topic: str, event_type: str, payload: dict):
    prod = await get_producer()
    if not prod:
        logger.debug("kafka not configured, dropping event")
        return
    msg = json.dumps({"event": event_type, "payload": payload}).encode("utf-8")
    await prod.send_and_wait(topic, msg)