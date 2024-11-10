from dataclasses import dataclass
import os
from typing import Any

from influxdb_client import InfluxDBClient, Point


@dataclass
class KeyValue:
    key: str
    value: Any

def get_client() -> InfluxDBClient:
    influxdb_url = os.getenv("INFLUXDB_URL")
    influxdb_token = os.getenv("INFLUXDB_TOKEN")
    influxdb_org = os.getenv("INFLUXDB_ORG")
    
    return InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)

def get_influx_bucket() -> str:
    influxdb_bucket = os.getenv("INFLUXDB_BUCKET")
    return influxdb_bucket
    
def write_point(measurement_name: str, tag: KeyValue, field: KeyValue) -> None:
    tag_key = tag.key
    tag_value = tag.value
    
    field_key = field.key
    field_value = field.value
    
    with get_client() as client:
        write_api = client.write_api()
        data = Point(measurement_name).tag(tag_key, tag_value).field(field_key, field_value)
        write_api.write(bucket=get_influx_bucket(), record=data)