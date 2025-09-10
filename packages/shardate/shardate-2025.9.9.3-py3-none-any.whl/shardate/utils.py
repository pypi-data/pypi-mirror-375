from pyspark.sql import Column
from pyspark.sql import functions as F


def date_col() -> Column:
    return F.to_date(F.concat_ws("-", "y", "m", "d")).alias("date")
