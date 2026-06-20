import json

import loguru
import redis

from .models import ShortURL, ClickEvent


def listen():

    client = redis.Redis(host="redis", port=6379, decode_responses=True,)

    pubsub = client.pubsub()
    pubsub.subscribe("clicks:enriched")

    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        data = json.loads(message["data"])
        loguru.logger.info(f"Received enriched click event: {data}")

        short_url = ShortURL.objects.get(short_code=data["short_code"])

        click = ClickEvent.objects.create(
            short_url=short_url,
            ip_address=data["ip_address"],
            user_agent=data["user_agent"],
            browser=data["browser"],
            os=data["os"],
            device_type=data["device"],
        )
        loguru.logger.info(f"Created click id={click.id}")
