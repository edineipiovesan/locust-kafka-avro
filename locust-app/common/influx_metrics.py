from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "N0_t4wAXGnFXXT7gltzVBp-Jz5yAbO7bWZSjf7z0Ta-to3nE5Nx2tB3TrME8VIGQJMzmsvvbzqJKXCnz4Tziqw=="
org = "my-organization"
bucket = "locust"

client = InfluxDBClient(url="http://localhost:8086", token=token)
write_api = client.write_api(write_options=ASYNCHRONOUS)


def influx_success_handler(request_type, name, response_time, response_length, **kwargs):
    """ additional request success handler to log statistics """
    print("sending success metrics")
    point = Point("mem") \
        .tag("host", "master") \
        .field("request_type", request_type) \
        .field("name", name) \
        .field("response_time", response_time) \
        .field("response_length", response_length) \
        .time(datetime.utcnow(), WritePrecision.NS)

    write_api.write("locust", "my-organization", point)


def influx_failure_handler(request_type, name, response_time, response_length, exception, **kwargs):
    """ additional request failure handler to log statistics """
    print("sending fail metrics")
    point = Point("mem") \
        .tag("host", "master") \
        .field("request_type", str(request_type)) \
        .field("name", str(name)) \
        .field("response_time", int(response_time)) \
        .field("response_length", int(response_length)) \
        .field("exception", str(exception)) \
        .time(datetime.utcnow(), WritePrecision.NS)

    write_api.write("locust", "my-organization", point)
