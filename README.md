# Weather-dependent personal recommentations

The API provides only current data on weather. Likely one will need to keep some reasonable history of measurements
for each user (say, 2 weeks) to make meaningful recommendations and improve ML models. So I would use some time-series
DBMS for that, and query this DB for recommendations. This way some recent weather or activity can be taken into
account.

Assuming Kafka sends all locations on same topic. It is possible to use topic-per-user instead, and Kafka now can handle
up to about 1M topics, but then we have to manage all these topics. Since location data comes at unpredictable moments,
the latest values are cached. If same {user, location} is requested frequently, the weather can also be cached. But then
one should decide when the data becomes invalid (too old weather data and/or significantly different location).
Currently relying on clients to decide whether data is too old already by looking at the timestamp (in that case they
should ignore it).
Using Postgres to store the location data (it could be e.g. Redis or Memcached instead). Keeping data in a persistent
volume helps to still be available after possible restarts (otherwise it would require to wait some time for the new
location data to come in).

Alternative implementation can keep (store persistently) the oldest Kafka offset that still provides actual location
data, and on startup restart from that offset filling cache. In this case the cache can be completely in-memory, but we
will not have older weather data points.

Tried using async, that is not necessary for the PoC, could have been a couple of threads instead.

Using [openmeteo](https://open-meteo.com/) service for weather data. Open-meteo can provide other weather measurements,
those can be added to the results if required.

# Setup, build, and run locally

Development requirements

* The instructions were tested on Linux.
* Shell scripts expect `bash` as interpreter.
* `virtualenv` is used for build and development.
* `docker`, `docker-compose` to run required external services
* `python3` (tested with CPython 3.10.12), pip

To prepare the environment and launch demo setup run `./run-demo.sh`.
To stop the script press ENTER.

To see current weather for a user run, for example, following

```shell
curl --silent http://127.0.0.1:8080/user/3/weather
```

Besides the API service itself the demo runs kafka as event bus, postgres for caching, and another Python script that
generates some fake locations for users and calls the service's API to see the result.

# TODO

* Currently, configuration is hard-coded (passwords, connection settings), this should be configurable (through a file
  or environment variables). Remove the secrets from sources.
* See how access to the service should be controlled (should it rely on Kubernetes or external proxy for that, or
  authentication/authorization should be handled by the service itself). Do we need HTTPS for the chosen setup?
* Build containers for the service and stubs.
* Integration/unit tests.
* Proper error handling. Errors should either terminate the service or give meaningful error message. The service should
  keep working after transient errors (e.g. when Kafka, postgres, or weather service are temporarily unavailable).
* Use a logger library, so messages from the libraries and from the service itself have the same format. Write
  timestamps in log messages.
* Formalize API. Recommendation service(s) will depend on weather format, so if something is there by accident it will
  be hard to remove later. Validate incoming messages, at least from our own services (Kafka).
* Likely the service will have to provide the history not only the most recent values (for export, ML training). In
  current form it can be done by running an external scraper.

# Ubuntu/Debian setup

The following may be needed to install on a Debian-like Linux distribution.

```
sudo apt install docker.io docker-compose-v2
```

Python and pip are likely to be already installed.

# CLI Notes

`kafkacat` can be used to send/inspect kafka events.

Sending example

```
kafkacat -P -b localhost:9092 -t user_weather -K :
key1:value1
key2:value2
```

Receiving example

```
kafkacat -C -b localhost:9092 -t user_weather -o beginning
```

# References

* [Kafka in Docker](https://medium.com/@tetianaokhotnik/setting-up-a-local-kafka-environment-in-kraft-mode-with-docker-compose-and-bitnami-image-enhanced-29a2dcabf2a9)
* [Postgres in Docker](https://hub.docker.com/_/postgres/)
* [Kafka CLI](https://codingharbour.com/apache-kafka/learn-how-to-use-kafkacat-the-most-versatile-cli-client/)
* [Open Meteo API](https://open-meteo.com/en/docs)
