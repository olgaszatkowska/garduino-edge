import logging
import os

import Adafruit_DHT
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
import digitalio
import board
import busio

from influxdb_client import Point
from datetime import datetime

from influx.client import LocalRawDBClient

IS_DHT11_CONNECTED = os.getenv("DHT11_CONNECTED") == "1"
IS_SEN0193_CONNECTED = os.getenv("SEN0193_CONNECTED") == "1"
SENSOR_MAX_VOLTAGE = 3.3

DHT_SENSOR = Adafruit_DHT.DHT11
SENSOR_1_PIN = 4
SENSOR_2_PIN = 17


class CollectDataService:
    def __init__(self) -> None:
        self.influxdb_client = LocalRawDBClient()

        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = digitalio.DigitalInOut(board.D8)
        mcp = MCP3008(spi, cs)

        self.sen0193_1 = AnalogIn(mcp, MCP3008.P0)
        self.sen0193_2 = AnalogIn(mcp, MCP3008.P1)

    def collect_data(self):
        if IS_DHT11_CONNECTED:
            try:
                self._collect_dht11_data()
            except:
                logging.error("Failed to gather data from dht11 sensor")

        if IS_SEN0193_CONNECTED:
            try:
                self._collect_sen0193_data()
            except:
                logging.error("Failed to gather data from sen0193 sensor")

    def _collect_dht11_data(self):
        """
        Collect data from air
        """
        current_time = datetime.now(datetime.timezone.utc)
        humidity_1, temperature_1 = Adafruit_DHT.read_retry(DHT_SENSOR, SENSOR_1_PIN)
        humidity_2, temperature_2 = Adafruit_DHT.read_retry(DHT_SENSOR, SENSOR_2_PIN)
        
        average_humidity = (humidity_1+humidity_2)/2
        average_temperature = (temperature_1+temperature_2)/2

        point = (
            Point("air_data")
            .tag("sensor_id", "dht11")
            .field("humidity", float(average_humidity))
            .field("temperature", float(average_temperature))
            .time(current_time)
        )

        self.influxdb_client.write_point(point)


    def _collect_sen0193_data(self):
        """
        Collect data from flower pots.
        Uses DFRobot Gravity.
        """

        humidity = lambda voltage: (voltage / SENSOR_MAX_VOLTAGE) * 100
        humidity_1 = humidity(self.sen0193_1.voltage)
        humidity_2 = humidity(self.sen0193_2.voltage)
        
        average_humidity = (humidity_1+humidity_2)/2

        current_time = datetime.now(datetime.timezone.utc)

        point = (
            Point("flower_pots_data")
            .tag("sensor_id", "sen0193")
            .field("humidity", average_humidity)
            .time(current_time)
        )

        self.influxdb_client.write_point(point)
