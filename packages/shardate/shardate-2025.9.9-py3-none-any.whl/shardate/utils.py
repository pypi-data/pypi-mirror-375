from pyspark.sql import functions as F


def date_col():
    return F.to_date(F.concat_ws("-", "y", "m", "d")).alias("date")