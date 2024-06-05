# Stubs for external services that produce and consume data for the location service.
import asyncio
from random import random

import httpx
from kafka import KafkaProducer
import json


async def geo_data_generator():
    producer = KafkaProducer(bootstrap_servers='localhost:29092',
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    while True:
        await asyncio.sleep(random() * 2)
        producer.send('user_location', {
            'lat': random() * 360 - 180,
            'lon': random() * 360
        })
        print("sent message")


async def geo_data_consumer():
    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.sleep(1.0)
            r = await client.get('https://www.example.com/')
            print(r)


async def main():
    await asyncio.gather(geo_data_generator(),
                         geo_data_consumer())


if __name__ == "__main__":
    asyncio.run(main())
