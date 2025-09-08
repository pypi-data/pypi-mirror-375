"""Shardate: Fast reader for YMD-partitioned Parquet files."""

import importlib.metadata

from shardate.read import read_between, read_by_date, read_by_dates

try:
    __version__ = importlib.metadata.version("shardate")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["read_between", "read_by_date", "read_by_dates"]
