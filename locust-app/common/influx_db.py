from influxdb_client import InfluxDBClient

# You can generate a Token from the "Tokens Tab" in the UI
token = "N0_t4wAXGnFXXT7gltzVBp-Jz5yAbO7bWZSjf7z0Ta-to3nE5Nx2tB3TrME8VIGQJMzmsvvbzqJKXCnz4Tziqw=="
org = "my-organization"
bucket = "locust"

client = InfluxDBClient(url="http://influxdb:8086", token=token)

