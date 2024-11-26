import os
from influxdb_client import Point

from app.influx.client import LocalDBClient, AWSDBClient


DRY_RUN_MODE = os.environ.get("DRY_RUN_MODE") == '1'

class AggregateDataService():
    def __init__(self,*, data_collection_interval: int, data_upload_interval:int) -> None:
        self.influxdb_client_local = LocalDBClient()
        self.influxdb_client_aws = AWSDBClient()
        
        self.data_upload_interval = data_upload_interval
        self.data_collection_interval = data_collection_interval
        
        
    def aggregate_and_store(
        self,
        measurement: str,
        field: str,
        aggregation_func: str = "mean",
        output_measurement: str = "aggregated_data"
    ):
        time_end = "now()",
        time_start=f"-{self.data_upload_interval}s",
        aggregate_period=f"{self.data_collection_interval}s",

        query = f"""
        from(bucket: "{self.bucket}")
            |> range(start: {time_start}, stop: {time_end})
            |> filter(fn: (r) => r._measurement == "{measurement}" and r._field == "{field}")
            |> aggregateWindow(every: {aggregate_period}, fn: {aggregation_func}, createEmpty: false)
        """
        result = self.client.query_api().query(org=self.org, query=query)

        aggregated_points = []
        for table in result:
            for record in table.records:
                point = (
                    Point(output_measurement)
                    .tag("source_measurement", measurement)
                    .field(field, record["_value"])
                    .time(record["_time"])
                )
                aggregated_points.append(point)
        
        if not DRY_RUN_MODE:
            self.influxdb_client_aws.write_point(aggregated_points)
        
        self.influxdb_client_local.write_point(aggregated_points)
    