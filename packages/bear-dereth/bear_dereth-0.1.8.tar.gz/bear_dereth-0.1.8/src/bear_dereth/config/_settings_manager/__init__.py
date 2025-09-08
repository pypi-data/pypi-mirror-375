"""A set of modules related to the settings manager."""

from ._db import Database, Table
from ._query import Query, where

__all__ = ["Database", "Query", "Table", "where"]
