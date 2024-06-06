# Stubs for external services that produce and consume data for the location service.
import asyncio
from random import random
from datetime import datetime
import httpx
import json
from aiokafka import AIOKafkaProducer
import asyncio


async def geo_data_generator():
    async with AIOKafkaProducer(bootstrap_servers='localhost:9092') as producer:
        await producer.start()
        while True:
            await asyncio.sleep(random() * 2)
            user_id = round(random() * 5)
            location = {
                'user_id': user_id,
                'ts': datetime.now().isoformat(),
                'lat': round(random() * 180 - 90, 5),
                'long': round(random() * 360 - 180, 5)
            }
            await producer.send_and_wait('user_location', json.dumps(location).encode('utf-8'))
            print(f"INFO [generator]  Set user #{user_id} location {location}")


async def geo_data_consumer():
    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.sleep(2.0)
            user_id = round(random() * 5)
            try:
                r = await client.get(f'http://127.0.0.1:8080/user/{user_id}/weather')
                print(f'INFO [client]  Get user #{user_id} location {r.json()}')
            except Exception as e:
                print(f'ERROR [client]  Get user #{user_id} location ERROR: {e}')


async def main():
    await asyncio.gather(geo_data_generator(),
                         geo_data_consumer())


if __name__ == "__main__":
    asyncio.run(main())
