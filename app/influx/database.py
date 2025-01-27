import os
from  influxdb_client import InfluxDBClient

from influx.abstract import DataBase


class LocalDB(DataBase):
    def get_client(self) -> InfluxDBClient:
        influxdb_url = os.getenv("DOCKER_INFLUXDB_URL")
        influxdb_token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN")
        influxdb_org = os.getenv("DOCKER_INFLUXDB_INIT_ORG")

        return InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org, timeout=30_000)

    def get_bucket(self) -> str:
        influxdb_bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")
        return influxdb_bucket


class LocalRawDB(LocalDB):
    def get_bucket(self) -> str:
        influxdb_bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET_RAW")
        return influxdb_bucket


class AWSDB(DataBase):
    def get_client(self) -> InfluxDBClient:
        influxdb_url = os.getenv("AWS_INFLUXDB_URL")
        influxdb_token = os.getenv("AWS_INFLUXDB_TOKEN")
        influxdb_org = os.getenv("DOCKER_INFLUXDB_INIT_ORG")

        return InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org, timeout=30_000)

    def get_bucket(self) -> str:
        influxdb_bucket = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET")
        return influxdb_bucket
