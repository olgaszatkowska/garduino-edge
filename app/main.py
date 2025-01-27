import os
from datetime import datetime

from sensors.collect_data import CollectDataService
from aggregate.aggregate_data import AggregateDataService
from logging_config import setup_logging

logging = setup_logging("main")


DATA_COLLECTION_INTERVAL_SECONDS = os.environ.get("DATA_COLLECTION_INTERVAL_SECONDS")
DATA_UPLOAD_INTERVAL_SECONDS = os.environ.get("DATA_UPLOAD_INTERVAL_SECONDS")

DHT11_CONNECTED = os.getenv("DHT11_CONNECTED")
SEN0193_CONNECTED = os.getenv("SEN0193_CONNECTED")


def check_env():
    if not (
        DATA_COLLECTION_INTERVAL_SECONDS
        or DATA_UPLOAD_INTERVAL_SECONDS
        or DHT11_CONNECTED
        or SEN0193_CONNECTED
    ):
        logging.error("Missing settings configuration. Please see readme.")
        raise Exception("Missing settings configuration. Please see readme.")


def main():
    data_collection_interval = int(DATA_COLLECTION_INTERVAL_SECONDS)
    data_upload_interval = int(DATA_UPLOAD_INTERVAL_SECONDS)
    
    logging.info(f"App start")
    
    aggregate_service = AggregateDataService(data_upload_interval=data_upload_interval, data_collection_interval=data_collection_interval)

    last_save_time = datetime.now()
    last_upload_time = datetime.now()

    while True:
        current_time = datetime.now()

        data_save_time_difference = current_time - last_save_time
        time_to_save = (
            data_save_time_difference.total_seconds() > data_collection_interval
        )
        if time_to_save:
            CollectDataService().collect_data()
            last_save_time = datetime.now()

        data_upload_time_difference = current_time - last_upload_time
        time_to_upload = (
            data_upload_time_difference.total_seconds() > data_upload_interval
        )

        if time_to_upload:
            if DHT11_CONNECTED == "1":
                logging.info(f"Aggregating data from DHT11")

                aggregate_service.aggregate_and_store(
                    measurement="air_data",
                    field="temperature",
                    output_measurement="aggregated_air_data"
                )
                aggregate_service.aggregate_and_store(
                    measurement="air_data",
                    field="humidity",
                    output_measurement="aggregated_air_data"
                )
                
            if SEN0193_CONNECTED == "1":
                logging.info(f"Aggregating data from SEN0193")

                aggregate_service.aggregate_and_store(
                    measurement="soil_data",
                    field="moisture",
                    output_measurement="aggregated_soil_data"
                )
            
            last_upload_time = datetime.now()


if __name__ == "__main__":
    check_env()
    main()
