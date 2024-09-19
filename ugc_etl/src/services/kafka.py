from aiokafka import AIOKafkaConsumer

from core.config import settings


async def consume():
    consumer = AIOKafkaConsumer(
        settings.kafka.topic,
        bootstrap_servers=[settings.kafka.bootstrap_server],
        auto_offset_reset="earliest",
        group_id="echo-messages-to-stdout",
        enable_auto_commit=False,
    )
    await consumer.start()
    try:
        while True:
            result = await consumer.getmany(
                timeout_ms=10 * 1000, max_records=1000
            )
            for tp, messages in result.items():
                if messages:
                    yield messages
                    # Commit progress only for this partition
                    await consumer.commit({tp: messages[-1].offset + 1})
    finally:
        await consumer.stop()
