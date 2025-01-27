import os

import adafruit_dht  
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import busio
import board

from influxdb_client import Point
from datetime import datetime, timezone

from influx.database import LocalRawDB
from logging_config import setup_logging

logging = setup_logging("collect_data")

IS_DHT11_CONNECTED = os.getenv("DHT11_CONNECTED") == "1"
IS_SEN0193_CONNECTED = os.getenv("SEN0193_CONNECTED") == "1"
SENSOR_MAX_VOLTAGE = 3.3


class CollectDataService:
    def __init__(self) -> None:
        self.db = LocalRawDB()
        
        if IS_DHT11_CONNECTED:
            self.dht_device_1 = adafruit_dht.DHT22(board.D23)
            self.dht_device_2 = adafruit_dht.DHT22(board.D24)
        
        if IS_SEN0193_CONNECTED:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS1115(self.i2c)
            
            self.sen0193_1 = AnalogIn(self.ads, 0)
            self.sen0193_2 = AnalogIn(self.ads, 1)

    def collect_data(self):
        if IS_DHT11_CONNECTED:
            try:
                self._collect_dht11_data()
            except Exception as e:
                logging.error("Failed to gather data from dht11 sensor")
                raise e

        if IS_SEN0193_CONNECTED:
            try:
                self._collect_sen0193_data()
            except Exception as e:
                logging.error("Failed to gather data from sen0193 sensor")
                raise e

    def _collect_dht11_data(self):
        """
        Collect data from air
        """
        current_time = datetime.now(timezone.utc)
        humidity_1, temperature_1 = self.dht_device_1.humidity, self.dht_device_1.temperature, 
        humidity_2, temperature_2 = self.dht_device_2.humidity, self.dht_device_2.temperature, 
        
        average_humidity = (humidity_1+humidity_2)/2
        average_temperature = (temperature_1+temperature_2)/2

        point = (
            Point("air_data")
            .tag("sensor_id", "dht11")
            .field("humidity", float(average_humidity))
            .field("temperature", float(average_temperature))
            .time(current_time)
        )
        
        logging.info(f"Collected humidity: {float(average_humidity)} and temperature: {float(average_temperature)}")

        self.db.write_point(point)


    def _collect_sen0193_data(self):
        """
        Collect data from soil.
        Uses DFRobot Gravity.
        """
        moisture = lambda voltage: (voltage / SENSOR_MAX_VOLTAGE) * 100
        v_1 = self.sen0193_1.voltage
        v_2 = self.sen0193_2.voltage
        
        logging.info(f"Voltage in soil sensors: {v_1} and {v_2}")
        
        moisture_1 = moisture(v_1)
        moisture_2 = moisture(v_2)
        
        average_moisture = (moisture_1+moisture_2)/2

        current_time = datetime.now(timezone.utc)

        point = (
            Point("soil_data")
            .tag("sensor_id", "sen0193")
            .field("moisture", average_moisture)
            .time(current_time)
        )
        
        logging.info(f"Collected moisture: {average_moisture}")

        self.db.write_point(point)
