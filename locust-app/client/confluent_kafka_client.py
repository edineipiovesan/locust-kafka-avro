import time
from uuid import uuid4

from confluent_kafka import SerializingProducer
from confluent_kafka.cimpl import TIMESTAMP_CREATE_TIME, Message
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from locust import events

from common.schema import MyAvroMessage


class KafkaAvroClient:

    def __init__(self, kafka_brokers=None, schema_registry=None):
        print("creating message sender with params: " + str(locals()))

        if kafka_brokers is None:
            kafka_brokers = ['localhost:9092']
        if schema_registry is None:
            schema_registry = 'http://localhost:8081'

        schema_registry_client = SchemaRegistryClient({'url': schema_registry})
        avro_serializer = AvroSerializer(schema_str=MyAvroMessage.schema_str,
                                         schema_registry_client=schema_registry_client,
                                         to_dict=MyAvroMessage.to_dict)

        configs = {
            'bootstrap.servers': ','.join(str(x) for x in kafka_brokers),
            'key.serializer': StringSerializer('utf_8'),
            'value.serializer': avro_serializer,
            'linger.ms': 1,  # wait for 1 ms until send event
            'message.timeout.ms': 1,
            'batch.size': 1,  # 18 = the same as topic partitions = the same parallelism as application; 0 = no batching
            'statistics.interval.ms': 3000,
            'stats_cb': self.__handle_statistics
        }

        self.avro_producer = SerializingProducer(configs)

    def __handle_statistics(self, stats=None):
        print("")

    def __handle_success(self, msg=None):
        try:
            msg_type, msg_timestamp = msg.timestamp()
            elapsed_millis = (time.time_ns() // 1000000) - msg_timestamp if msg_type == TIMESTAMP_CREATE_TIME else 0
            request_data = dict(request_type="Kakfa Client",
                                name=msg.topic(),
                                response_time=elapsed_millis,
                                response_length=len(msg.value()))

            self.__fire_success(**request_data)
        except Exception as ex:
            print("Logging the exception : {0}".format(ex))
            raise  # ??

    def __handle_failure(self, msg=None, err=None):
        # print("__handle_failure " + str(locals()))
        try:
            msg_type, msg_timestamp = msg.timestamp()
            elapsed_millis = (time.time_ns() // 1000000) - msg_timestamp if msg_type == TIMESTAMP_CREATE_TIME else 0
            request_data = dict(request_type="Kakfa Client",
                                name=msg.topic(),
                                response_time=elapsed_millis,
                                response_length=len(msg.value()),
                                exception=err)

            self.__fire_failure(**request_data)
        except Exception as ex:
            print("Logging the exception : {0}".format(ex))
            raise  # ??

    def __fire_failure(self, **kwargs):
        events.request_failure.fire(**kwargs)

    def __fire_success(self, **kwargs):
        events.request_success.fire(**kwargs)

    def __handle_callback(self, err, msg):
        if err is not None:
            self.__handle_failure(err=err, msg=msg)
        else:
            self.__handle_success(msg=msg)

    def send(self, topic, key=None, message=None):
        if key is None:
            key = str(uuid4())
        value = MyAvroMessage(name=message, type="Message")

        try:
            self.avro_producer.produce(topic=topic, key=key, value=value, on_delivery=self.__handle_callback)
            self.avro_producer.flush()
        except Exception as err:
            self.__fire_failure(**dict(
                request_type="Kakfa Client",
                name=topic,
                response_time=0.0,
                response_length=len(MyAvroMessage.to_dict(value=value, ctx=None))
            ), exception=err)

    def finalize(self):
        self.avro_producer.flush()
