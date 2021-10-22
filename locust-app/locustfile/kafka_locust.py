import os
import time
from uuid import uuid4

from locust import TaskSet, task, events, User, constant

from client.confluent_kafka_client import KafkaAvroClient as KafkaClient
from common.influx_metrics import influx_success_handler, influx_failure_handler

# read kafka brokers from config
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "broker:29092").split(sep=",")
SCHEMA_REGISTRY = os.getenv("SCHEMA_REGISTRY", "http://schema-registry:8081")

# build kafka client
# KAFKA_CLIENT = KafkaClient(kafka_brokers=KAFKA_BROKERS, schema_registry=SCHEMA_REGISTRY)
KAFKA_CLIENT = KafkaClient()

# # read other environment variables
# SEND_METRICS = True if os.getenv("SEND_METRICS", "false").lower() in ['1', 'true', 'yes'] else False
#
# # register additional logging handlers
# if not SEND_METRICS:
events.request_success.add_listener(influx_success_handler)
events.request_failure.add_listener(influx_failure_handler)


class UserTasks(TaskSet):
    wait_time = constant(1)

    def timestamped_message(self):
        return f"[{time.time() * 1000}]: This is a message sent by Locust."

    @task
    def publish_charge_events(self):
        self.client.send("locust.avro.output", message=self.timestamped_message(), key=str(uuid4()))

    # @task
    # def get_charge(self):
    #     self.client.get()


class ChargeUser(User):
    client = None

    # http_client = None

    def __init__(self, *args, **kwargs):
        super(ChargeUser, self).__init__(*args, **kwargs)

        if not ChargeUser.client:
            ChargeUser.client = KAFKA_CLIENT
        # if not ChargeUser.http_client:
        #     ChargeUser.http_client = None  # TODO: set http client

    tasks = {UserTasks}
