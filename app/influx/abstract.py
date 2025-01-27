from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from influxdb_client import Point


@dataclass
class KeyValue:
    key: str
    value: Any


class DataBase(ABC):
    """
    Abstract base class for a DataBase.
    """

    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def get_bucket(self):
        pass

    def write_point(self, point: Point | list[Point]) -> None:
        with self.get_client() as client:
            write_api = client.write_api()
            write_api.write(bucket=self.get_bucket(), record=point)
