from typing import Union
import asyncio

from open_meteo import OpenMeteo
from threading import Thread
import json
from aiokafka import AIOKafkaConsumer
import asyncpg
from datetime import datetime
from fastapi import FastAPI
import uvicorn


def connect_db():
    return asyncpg.connect(user='postgres', password='notasecret',
                           database='postgres', host='127.0.0.1')


async def setup_database(conn):
    # The data is transient, so we can re-create database at any time.
    # If we'll have any data that is worth to keep, then we should use DB migrations instead.
    try:
        await conn.fetch('select count(*) from recent_user_location')
        print("INFO [db-setup]  DB table recent_user_location found.")
    except Exception as e:
        await conn.execute('''
            create table recent_user_location(
                user_id integer primary key,
                ts timestamptz,
                lat real,
                long real
            )
        ''')
        print("INFO [db-setup]  DB table recent_user_location created.")


async def user_location_update():
    conn = await connect_db()
    await setup_database(conn)
    async with AIOKafkaConsumer(
            'user_location',
            bootstrap_servers='localhost:9092',
            group_id="user_weather") as consumer:
        while True:
            async for msg in consumer:
                location = json.loads(msg.value)
                print(f"INFO [kafka-consumer]  Got location {location}")
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


async def find_user_location(user_id: int) -> Union[dict, None]:
    conn = await connect_db()
    try:
        r = await conn.fetch('select ts, lat, long from recent_user_location where user_id=$1', user_id)
        try:
            location = r[0]
        except IndexError:
            return None
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
    if location is None:
        return None
    return await weather_for_location(location['lat'], location['long'])


app = FastAPI()


@app.get("/")
async def read_root():
    return "OK"


@app.get("/user/{user_id}/weather")
async def read_item(user_id: int):
    weather = await get_weather_for_user(user_id)
    print(f'DEBUG [api]  User #{user_id} weather is {weather}.')
    return {'user_id': user_id, 'weather': weather}


def asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(user_location_update())


def run_fastapi():
    uvicorn.run(app, host='127.0.0.1', port=8080)


if __name__ == "__main__":
    t = Thread(target=run_fastapi, daemon=True)
    t.start()
    asyncio.run(user_location_update())
