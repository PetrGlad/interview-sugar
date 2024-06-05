from typing import Union
import asyncio

from open_meteo import OpenMeteo
from open_meteo.models import DailyParameters, HourlyParameters
from flask import Flask


async def find_user_location(user_id: str) -> Union[dict, None]:
    # TODO Read the most recent event from Kafka
    return


async def weather_for_location(lat: float, long: float) -> Union[dict, None]:
    """Show example on using the Open-Meteo API client."""
    async with OpenMeteo() as open_meteo:
        forecast = await open_meteo.forecast(
            latitude=52.27,
            longitude=6.87417,
            current_weather=True,
            daily=[
                DailyParameters.SUNRISE,
                DailyParameters.SUNSET,
            ],
            hourly=[
                HourlyParameters.TEMPERATURE_2M,
                HourlyParameters.RELATIVE_HUMIDITY_2M,
            ],
        )
        print(forecast)
        print(forecast.current_weather.__dict__)
        print(forecast.json())
        return {'temperature': 13.34}  # FIXME Stub


async def get_weather_for_user(user_id: str) -> Union[dict, None]:
    location = await find_user_location(user_id)
    await weather_for_location()
    raise Exception("Not implemented") # FIXME Stub


app = Flask(__name__)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    app.run(debug=True, port=8080)
