#!/bin/bash
set -e -x
cd "$(dirname "$0")"

virtualenv venv
. ./venv/bin/activate
pip3 install -r requirements.txt

docker compose up -d
echo "Waiting for services to come up..."
sleep 10s

trap 'kill $STUBS_PID ; kill $API_PID ; docker compose down ; exit 0' SIGINT SIGTERM EXIT

python3 src/integration_stubs.py &
STUBS_PID=$!
python3 src/user_weather.py &
API_PID=$!

echo "Press ENTER to exit."
read
