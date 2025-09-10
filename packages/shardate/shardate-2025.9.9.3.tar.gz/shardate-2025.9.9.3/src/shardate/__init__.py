"""Shardate: Fast reader for YMD-partitioned Parquet files."""

import importlib.metadata

from .shardate import Shardate

try:
    __version__ = importlib.metadata.version("shardate")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["Shardate"]
