import os

from influx.abstract import Client, InfluxDBClient


class LocalDBClient(Client):
    def get_client() -> InfluxDBClient:
        influxdb_url = os.getenv("INFLUXDB_URL")
        influxdb_token = os.getenv("INFLUXDB_TOKEN")
        influxdb_org = os.getenv("INFLUXDB_ORG")

        return InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)

    def get_influx_bucket() -> str:
        influxdb_bucket = os.getenv("INFLUXDB_BUCKET")
        return influxdb_bucket


class LocalRawDBClient(Client):
    def get_influx_bucket() -> str:
        influxdb_bucket = os.getenv("INFLUXDB_BUCKET_RAW")
        return influxdb_bucket


class AWSDBClient(Client):
    def get_client() -> InfluxDBClient:
        influxdb_url = os.getenv("AWS_INFLUXDB_URL")
        influxdb_token = os.getenv("AWS_INFLUXDB_TOKEN")
        influxdb_org = os.getenv("INFLUXDB_ORG")

        return InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)

    def get_influx_bucket() -> str:
        influxdb_bucket = os.getenv("INFLUXDB_BUCKET")
        return influxdb_bucket
