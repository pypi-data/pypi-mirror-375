from pyspark.sql import SparkSession
from dataclasses import dataclass
from shardate.dates import all_dates_between, eoms_between


def spark_session():
    try:
        return SparkSession.getActiveSession()
    except Exception as e:
        raise RuntimeError("No active SparkSession found. Please create one.") from e


@dataclass
class Shardate:
    path: str
    partition_format: str = "y=%Y/m=%m/d=%d"

    @property
    def read_parquet(self):
        return spark_session().read.options(basePath=self.path).parquet

    def read_by_date(self, target_date):
        return self.read_parquet(
            f"{self.path}/{target_date.strftime(self.partition_format)}"
        )

    def read_between(self, start_date, end_date):
        return self.read_parquet(
            *{
                f"{self.path}/{dt.strftime(self.partition_format)}"
                for dt in all_dates_between(start_date, end_date)
            }
        )

    def read_by_dates(self, target_dates):
        return self.read_parquet(
            *{
                f"{self.path}/{dt.strftime(self.partition_format)}"
                for dt in target_dates
            }
        )

    def read_eoms_between(self, start_date, end_date):
        return self.read_by_dates(eoms_between(start_date, end_date))
