import json, logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)
_producer = None

async def get_producer():
    global _producer
    if _producer is None:
        servers = settings.kafka_bootstrap_service or ""
        if not servers:
            return None
        _producer = AIOKafkaProducer(bootstrap_servers=[s.strip() for s in servers.split(",")])
        await _producer.start()
    return _producer

async def publish_event(topic: str, event_type: str, payload: dict):
    prod = await get_producer()
    if not prod:
        logger.debug("kafka disabled - drop event")
        return
    msg = json.dumps({"event": event_type, "payload": payload}).encode()
    await prod.send_and_wait(topic, msg)