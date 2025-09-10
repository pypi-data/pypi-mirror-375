from datetime import date
from shardate.dates import all_dates_between, is_end_of_month, eoms_between


def test_all_dates_between():
    res = all_dates_between(date(2025, 12, 31), date(2026, 1, 3))
    expected = [
        date(2025, 12, 31),
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 3),
    ]
    assert list(res) == expected


def test_is_end_of_month():
    assert is_end_of_month(date(2026, 1, 31))
    assert not is_end_of_month(date(2026, 1, 30))


def test_eoms_between():
    res = eoms_between(date(2025, 12, 29), date(2026, 2, 2))
    expected = [date(2025, 12, 31), date(2026, 1, 31)]
    assert list(res) == expected
