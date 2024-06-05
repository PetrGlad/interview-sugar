# Weather-dependent personal recommentations

Using [openmeteo](https://open-meteo.com/) service for weather data.

# Setup, build, and run locally


Dev setup using virtual environment
```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```


Local development or demo setup. The instrustions use podman. Docker commands houls be idencical.

```
./run-demo.sh
```

# Ubuntu/Debian setup

sudo apt install kafkacat docker.io docker-compose-v2


# Some useful CLI tools


Sending
```
kafkacat -P -b localhost:29092 -t topic1 -K :
key1:value1
key2:value2
```

Reading
```
kafkacat -C -b localhost:29092 -t topic1 -o beginning
```



# References

* [Kafka Docker](https://www.baeldung.com/ops/kafka-docker-setup)
* [Kafka CLI](https://codingharbour.com/apache-kafka/learn-how-to-use-kafkacat-the-most-versatile-cli-client/)
* [OPen Meteo API](https://open-meteo.com/en/docs)
