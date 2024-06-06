# Weather-dependent personal recommentations

Using [openmeteo](https://open-meteo.com/) service for weather data.

The service provides only current data on weather. Likely one will need to keep some reasonable history of measurements
for each user (say, 2 weeks) to make meaningful recommendations and improve ML models. So I would use some time-series
DBMS for that, and query this DB for recommendations (so, for example also some recent weather or activity can be
taken into account).

Assuming Kafka sends all locations on same topic. It is possible to use topic-per-user instead, and Kafka now can handle
up to about 1M topics, but then we have to manage all these topics. Since location data comes at unpredictable moments,
the latest values are cached. If same {user, location} is requested frequently, the weather can also be cached. But then
one shoulid decide when the data becomes invalid (too old weather data and/or significantly different location).
Currently relying on clients to decide whether data is too old already looking at the timestamp (in that case they
should ignore it).
Using Postgres to store the location data (it could be e.g. Redis or Memcached instead). Keeping data in a persistent
volume helps to still be available after possible restarts (otherwise it would require to wait some time for the new
location data to come in).

Alternative implementation can keep (store persitently) the oldest Kafka offset that still provides actual location
data, and on startup restart from that offset filling cache. In this case the cache can be completely in-memory, but we
will not have older weather data points.

Tried using async, that is not necessary for the PoC, could have been a couple of threads instead.

Openmeteo can provide other weather measurements, those can be added if required.

# Setup, build, and run locally

Dev setup using virtual environment

```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

To run demo setup run the `./run-demo.sh` script.

# TODO

* Currently, configuration is hard-coded (passwords, connection settings), this should be configurable (throug a file or
  environment variables). Remove the secrets from sources.
* See how access to the service should be controlled (should it rely on Kubernetes or external proxy for that, or
  authenitcation/authorization should be handled by the service). Do we need HTTPS for the chosen setup?
* Build containers for the service and stubs.
* Integration/unit tests.
* Proper error handling. Errors should either terminate the service or give meaningful error message. The service should
  keep working after transient errors.
* Use a logger library, so messages from the libraries and from the service itself have the same format. Write
  timestamps in log messages.
* Formalize API. Recommendation service(s) will depend on weather format, so if something is there by accident it will
  be hard to remove later. Validate incoming messages, at least from our own servies (Kafka).
* Likely the service will have to provide the history not only the most recent values (for export, ML training). In
  current form it can be done by running an external scraper.

# Ubuntu/Debian setup

sudo apt install docker.io docker-compose-v2

# CLI Notes

Sending

```
kafkacat -P -b localhost:9092 -t topic1 -K :
key1:value1
key2:value2
```

Reading

```
kafkacat -C -b localhost:29092 -t topic1 -o beginning
```

# References

* [Kafka in Docker](https://medium.com/@tetianaokhotnik/setting-up-a-local-kafka-environment-in-kraft-mode-with-docker-compose-and-bitnami-image-enhanced-29a2dcabf2a9)
* [Postgres in Docker](https://hub.docker.com/_/postgres/)
* [Kafka CLI](https://codingharbour.com/apache-kafka/learn-how-to-use-kafkacat-the-most-versatile-cli-client/)
* [Open Meteo API](https://open-meteo.com/en/docs)

