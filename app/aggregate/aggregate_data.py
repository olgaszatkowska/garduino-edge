import os
from influxdb_client import Point

from influx.database import LocalDB, AWSDB, LocalRawDB
from logging_config import setup_logging

logging = setup_logging("aggregate")


DRY_RUN_MODE = os.environ.get("DRY_RUN_MODE") == '1'

class AggregateDataService():
    def __init__(self,*, data_collection_interval: int, data_upload_interval:int) -> None:
        self.local_db = LocalDB()
        self.local_raw_db = LocalRawDB()
        self.aws_db = AWSDB()
        
        self.data_upload_interval = data_upload_interval
        self.data_collection_interval = data_collection_interval
        
        self.failed_uploads = []

    def aggregate_and_store(
        self,
        measurement: str,
        field: str,
        aggregation_func: str = "mean",
        output_measurement: str = "aggregated_data"
    ):
        if self.failed_uploads:
            self._retry_failed_uploads()

        time_end = "now()"
        time_start=f"-{self.data_upload_interval}s"
        aggregate_period=f"{self.data_collection_interval}s"

        raw_bucket_name = self.local_raw_db.get_bucket()

        query = f"""
        from(bucket: "{raw_bucket_name}")
            |> range(start: {time_start}, stop: {time_end})
            |> filter(fn: (r) => r._measurement == "{measurement}" and r._field == "{field}")
            |> aggregateWindow(every: {aggregate_period}, fn: {aggregation_func}, createEmpty: false)
        """
        logging.info(query)
        raw_db_client = self.local_raw_db.get_client()
        query_api = raw_db_client.query_api()
        result = query_api.query(org=raw_db_client.org, query=query)

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
            try:
                self.aws_db.write_point(aggregated_points)
            except Exception as e:
                logging.error(f"Faled to upload aggregated data to cloud provider. Error: {e}")
                self.failed_uploads.extend(aggregated_points)
        
        self.local_db.write_point(aggregated_points)
    
    def _retry_failed_uploads(self):
        try:
            self.aws_db.write_point(self.failed_uploads)
        except Exception as e:
            logging.error(f"Faled to reupload aggregated data to cloud provider. Error: {e}")
            return
        
        self.failed_uploads = []
        logging.info(f"Succesfully uploaded failed uploads to cloud provider. Error: {e}")
