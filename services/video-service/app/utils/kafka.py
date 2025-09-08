import asyncio
import json
import logging
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import Optional, Callable, Awaitable

logger = logging.getLogger(__name__)


class KafkaClient:
    def __init__(self, bootstrap_servers: str, group_id: str = "default-group"):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None

    async def start_producer(self):
        if self.producer:
            return
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()
        logger.info("Kafka producer started.")

    async def stop_producer(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped.")

    async def send(self, topic: str, message: dict):
        if not self.producer:
            await self.start_producer()
        try:
            await self.producer.send_and_wait(topic, message)
            logger.debug(f"Message sent to {topic}: {message}")
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {e}")

    async def start_consumer(
        self,
        topic: str,
        handler: Callable[[dict], Awaitable[None]],
        auto_offset_reset: str = "earliest",
    ):
        if self.consumer:
            return
        self.consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset=auto_offset_reset,
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started on topic {topic}.")
        asyncio.create_task(self._consume_loop(handler))

    async def _consume_loop(self, handler: Callable[[dict], Awaitable[None]]):
        try:
            async for msg in self.consumer:
                try:
                    await handler(msg.value)
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")
        finally:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped.")   