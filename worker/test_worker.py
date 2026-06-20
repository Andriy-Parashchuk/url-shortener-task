import asyncio
import json

import fakeredis
import pytest

from main import enrich_click_event, process_event


@pytest.mark.asyncio
async def test_pubsub():

    redis_client = fakeredis.aioredis.FakeRedis(
        decode_responses=True
    )

    pubsub = redis_client.pubsub()

    await pubsub.subscribe("clicks:raw")
    await pubsub.get_message(timeout=1)

    await redis_client.publish(
        "clicks:raw",
        '{"short_url": "abc"}'
    )

    await asyncio.sleep(0.1)

    message = await pubsub.get_message(
        ignore_subscribe_messages=True,
        timeout=1
    )

    assert message is not None
    assert message["data"] == '{"short_url": "abc"}'


def test_enrich_event():

    event = {
        "short_code": "abc123",
        "ip_address": "127.0.0.1",
        "user_agent":
            "Mozilla/5.0 "
            "Chrome/120.0.0.0"
    }

    enriched = enrich_click_event(event)

    assert enriched["browser"]
    assert enriched["os"]
    assert enriched["device"]


@pytest.mark.asyncio
async def test_worker_processes_event():

    redis_client = fakeredis.aioredis.FakeRedis(
        decode_responses=True
    )

    enriched_pubsub = redis_client.pubsub()

    await enriched_pubsub.subscribe(
        "clicks:enriched"
    )

    await enriched_pubsub.get_message(timeout=1)

    event = {
        "short_code": "abc123",
        "ip_address": "127.0.0.1",
        "user_agent":
            "Mozilla/5.0 Chrome/120.0",
    }

    await process_event(
        redis_client,
        json.dumps(event)
    )

    message = await enriched_pubsub.get_message(
        ignore_subscribe_messages=True,
        timeout=1
    )
    await asyncio.sleep(0.1)

    assert message is not None

    payload = json.loads(
        message["data"]
    )

    assert payload["short_code"] == "abc123"
    assert "browser" in payload
    assert "os" in payload
