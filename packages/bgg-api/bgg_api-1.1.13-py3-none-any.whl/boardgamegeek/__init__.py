"""
.. module:: boardgamegeek
   :platform: Unix, Windows
   :synopsis: interface to boardgamegeek.com

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""

from .api import (
    BGGChoose,
    BGGClient,
    BGGRestrictCollectionTo,
    BGGRestrictDomainTo,
    BGGRestrictPlaysTo,
    BGGRestrictSearchResultsTo,
)
from .cache import CacheBackendMemory, CacheBackendNone, CacheBackendSqlite
from .exceptions import (
    BGGApiError,
    BGGApiRetryError,
    BGGApiTimeoutError,
    BGGError,
    BGGItemNotFoundError,
    BGGValueError,
)
from .legacy_api import BGGClientLegacy


__all__ = (
    "BGGClient",
    "BGGClientLegacy",
    "BGGChoose",
    "BGGRestrictSearchResultsTo",
    "BGGRestrictPlaysTo",
    "BGGRestrictDomainTo",
    "BGGRestrictCollectionTo",
    "BGGError",
    "BGGValueError",
    "BGGApiRetryError",
    "BGGApiError",
    "BGGApiTimeoutError",
    "BGGItemNotFoundError",
    "CacheBackendNone",
    "CacheBackendSqlite",
    "CacheBackendMemory",
)

__version__ = "1.1.13"
