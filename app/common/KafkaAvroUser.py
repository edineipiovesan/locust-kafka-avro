import functools
import time
from pathlib import Path

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from locust import User


class KafkaAvroUser(User):
    abstract = True
    # overload these values in your subclass
    bootstrap_servers: str = None  # type: ignore

    def __init__(self, environment):
        super().__init__(environment)
        self.client: KafkaClient = KafkaClient(environment=environment, bootstrap_servers=self.bootstrap_servers)

    def on_stop(self):
        self.client.producer.flush(5)


def _on_delivery(environment, identifier, response_length, start_time, start_perf_counter, context, err, _msg):
    environment.events.request.fire(
        request_type="ENQUEUE",
        name=identifier,
        start_time=start_time,
        response_time=(time.perf_counter() - start_perf_counter) * 1000,
        response_length=response_length,
        context=context,
        exception=err,
    )


class KafkaClient:
    def __init__(self, *, environment, bootstrap_servers):
        self.environment = environment
        # schema = Path('avro/client_identifier.avsc').read_text()
        schema = """
{
   "type":"record",
   "name":"ClientIdentifier",
   "namespace":"com.baeldung.avro",
   "fields":[
      { "name":"hostName", "type":"string" },
      { "name":"ipAddress", "type":"string" }
   ]
}
        """
        schema_registry_client = SchemaRegistryClient({'url': 'http://schema-registry:8081'})
        avro_serializer = AvroSerializer(schema_registry_client=schema_registry_client, schema_str=schema)
        self.producer = SerializingProducer({
            'bootstrap.servers': bootstrap_servers,
            'key.serializer': StringSerializer('utf_8'),
            'value.serializer': avro_serializer,
            'linger.ms': 100,
            'batch.size': 1000,
            'statistics.interval.ms': 1000
        })

    def send(self, topic: str, value: bytes, key=None, response_length_override=None, name=None, context={}):
        start_perf_counter = time.perf_counter()
        start_time = time.time()
        identifier = name if name else topic
        response_length = response_length_override if response_length_override else len(value)
        callback = functools.partial(
            _on_delivery, self.environment, identifier, response_length, start_time, start_perf_counter, context
        )
        self.producer.produce(topic, value, key, on_delivery=callback)
        # self.producer.poll()
