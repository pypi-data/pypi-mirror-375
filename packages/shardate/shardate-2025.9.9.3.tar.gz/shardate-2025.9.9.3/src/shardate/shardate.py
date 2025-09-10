from datetime import date
from typing import Iterable, Callable, Any

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from dataclasses import dataclass

from shardate.dates import all_dates_between, eoms_between


def spark_session() -> SparkSession:
    if session := SparkSession.getActiveSession():
        return session
    raise RuntimeError("No active SparkSession found. Please create one.")


@dataclass
class Shardate:
    path: str
    partition_format: str = "y=%Y/m=%m/d=%d"

    @property
    def read(self) -> Callable[[Any], DataFrame]:
        return spark_session().read.options(basePath=self.path).parquet

    def read_by_date(self, target_date: date) -> DataFrame:
        return self.read(
            f"{self.path}/{target_date.strftime(self.partition_format)}"
        )

    def read_between(self, start_date: date, end_date: date) -> DataFrame:
        return self.read(
            *{
                f"{self.path}/{dt.strftime(self.partition_format)}"
                for dt in all_dates_between(start_date, end_date)
            }
        )

    def read_by_dates(self, target_dates: Iterable[date]) -> DataFrame:
        return self.read(
            *{
                f"{self.path}/{dt.strftime(self.partition_format)}"
                for dt in target_dates
            }
        )

    def read_eoms_between(self, start_date: date, end_date: date) -> DataFrame:
        return self.read_by_dates(eoms_between(start_date, end_date))
