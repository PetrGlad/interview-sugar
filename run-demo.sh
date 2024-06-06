#!/bin/bash
set -e -x
cd "$(dirname "$0")"

. ./venv/bin/activate

docker compose up -d

python src/integration_stubs.py &

python src/user_weather.py
