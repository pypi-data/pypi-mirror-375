from dateutil.relativedelta import relativedelta


def all_dates_between(start_date, end_date):
    return (
        start_date + relativedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    )


def is_end_of_month(dt):
    return dt == dt + relativedelta(day=1, months=1, days=-1)


def eoms_between(start_date, end_date):
    return [i for i in all_dates_between(start_date, end_date) if is_end_of_month(i)]
