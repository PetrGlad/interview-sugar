from typing import Union
import asyncio

from open_meteo import OpenMeteo
# from open_meteo.models import DailyParameters, HourlyParameters
from flask import Flask
from threading import Thread
import json
from aiokafka import AIOKafkaConsumer
import asyncpg
from datetime import datetime
from fastapi import FastAPI
import uvicorn


async def setup_database(conn):
    # A poor man's DB migration.
    try:
        await conn.fetch('select count(*) from recent_user_location')
        print("INFO:  DB table recent_user_location found.")
    except Exception as e:
        await conn.execute('''
            create table recent_user_location(
                user_id integer primary key,
                ts timestamptz,
                lat real,
                long real
            )
        ''')
        print("INFO:  DB table recent_user_location created.")


def connect_db():
    return asyncpg.connect(user='postgres', password='notasecret',
                           database='postgres', host='127.0.0.1')


async def user_location_update():
    conn = await connect_db()
    await setup_database(conn)
    async with AIOKafkaConsumer(
            'user_location',
            bootstrap_servers='localhost:9092',
            group_id="user_weather") as consumer:
        while True:
            async for msg in consumer:
                print("consumed: ", msg.topic, msg.partition, msg.offset,
                      msg.key, msg.value, msg.timestamp)
                location = json.loads(msg.value)
                print(f"I Got location {location}")
                await conn.execute(
                    '''
                    insert into recent_user_location(user_id, ts, lat, long)
                    values ($1, $2, $3, $4)
                    on conflict (user_id) do update set ts = $2, lat = $3, long = $4
                ''',
                    location['user_id'],
                    datetime.fromisoformat(location['ts']),
                    float(location['lat']),
                    float(location['long']))


async def find_user_location(user_id: int) -> dict:
    conn = await connect_db()
    try:
        r = await conn.fetch('select ts, lat, long from recent_user_location where user_id=$1', user_id, )
        location = r[0]
        print(f'Query results #{user_id}: {r}')
        return {'lat': location['lat'], 'long': location['long']}
    finally:
        await conn.close()


async def weather_for_location(lat: float, long: float) -> Union[dict, None]:
    async with OpenMeteo() as open_meteo:
        forecast = await open_meteo.forecast(
            latitude=lat,
            longitude=long,
            current_weather=True,
        )
        return forecast.current_weather


async def get_weather_for_user(user_id: int) -> Union[dict, None]:
    location = await find_user_location(user_id)
    return await weather_for_location(location['lat'], location['long'])


app = FastAPI()


@app.get("/")
async def read_root():
    return "OK"


@app.get("/user/{user_id}/weather")
async def read_item(user_id: int):
    weather = await get_weather_for_user(user_id)
    print(f'RETURNING WEATHER: {weather}')
    return {'user_id': user_id, 'weather': weather}


def asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(user_location_update())


if __name__ == "__main__":
    t = Thread(target=asyncio_loop)
    t.start()
    uvicorn.run(app, host='127.0.0.1', port=8080)
