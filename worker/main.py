import asyncio
import json

import redis.asyncio as redis

from loguru import logger
from user_agents import parse

redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True,
)


async def process_event(data):
    event = json.loads(data)
    user_agent = parse(event["user_agent"])

    click_event = {
        **event,
        "short_code": event["short_code"],
        "ip_address": event["ip_address"],
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "device": user_agent.device.family,
    }

    logger.info(f"Processed click event: {click_event}")
    await redis_client.publish("clicks:enriched", json.dumps(click_event))


async def main():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("clicks:raw")
    logger.info("Subscribed to Redis channel 'clicks:raw'")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        asyncio.create_task(process_event(message['data']))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
