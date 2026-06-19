import asyncio
import json

from loguru import logger
from user_agents import parse

from redis_service import get_redis_client

redis_client = get_redis_client()


def enrich_click_event(event):
    user_agent = parse(event["user_agent"])

    return {
        **event,
        "short_code": event["short_code"],
        "ip_address": event["ip_address"],
        "browser": user_agent.browser.family,
        "os": user_agent.os.family,
        "device": user_agent.device.family,
    }


async def process_event(redis_client, data):
    event = json.loads(data)
    click_event = enrich_click_event(event)
    logger.info(f"Processed click event: {click_event}")
    await redis_client.publish("clicks:enriched", json.dumps(click_event))


async def main():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("clicks:raw")
    logger.info("Subscribed to Redis channel 'clicks:raw'")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        asyncio.create_task(process_event(redis_client, message['data']))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
