from datetime import date
from typing import Iterable
from dateutil.relativedelta import relativedelta


def all_dates_between(start_date: date, end_date: date) -> Iterable[date]:
    return (
        start_date + relativedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    )


def is_end_of_month(dt: date) -> bool:
    return dt == dt + relativedelta(day=1, months=1, days=-1)


def eoms_between(start_date: date, end_date: date) -> Iterable[date]:
    return (i for i in all_dates_between(start_date, end_date) if is_end_of_month(i))
