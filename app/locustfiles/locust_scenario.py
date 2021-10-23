import uuid

from locust import task

from common.KafkaAvroUser import KafkaAvroUser


class MyUser(KafkaAvroUser):
    # bootstrap_servers = os.environ["LOCUST_KAFKA_SERVERS"]
    bootstrap_servers = "broker:29092"

    @task
    def t(self):
        payload = f'{{"hostName": "host-{uuid.uuid4()}", "ipAddress": "localhost"}}'
        self.client.send("lafp_test", bytes(payload, 'utf-8'))
