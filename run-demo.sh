#!/bin/bash
set -e -x
cd "$(dirname "$0")"

virtualenv venv
. ./venv/bin/activate
pip3 install -r requirements.txt

docker compose up -d
python3 src/integration_stubs.py &
STUBS_PID=$!
fastapi dev src/user_weather.py

kill -9 $STUBS_PID