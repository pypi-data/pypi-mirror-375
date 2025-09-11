"""
Expressipy: OtakuGIFs API Wrapper
~~~~~~~~~~~~~~~~~~~~~

A basic wrapper for the OtakuGIFs API.

:copyright: (c) 2025-present AndehUK
:license: MIT, see LICENSE for more details.

"""

from __future__ import annotations

__version__ = "2.0.1"
__author__ = "AndehUK"
__title__ = "expressipy"
__description__ = "A fully typed, async API wrapper for OtakuGIFs API"
__license__ = "MIT"
__copyright__ = "Copyright 2025-present AndehUK"
__url__ = "https://github.com/AndehUK/expressipy"

from .client import ExpressipyClient
from .enums import ReactionType
from .exceptions import BadRequest, ExpressipyException, HTTPException, NotFound
from .http import HTTPClient
from .models import AllReactionsResponse, GifResponse
from . import utils as utils, types as types

__all__ = (
    "ExpressipyClient",
    "ReactionType",
    "BadRequest",
    "ExpressipyException",
    "HTTPException",
    "NotFound",
    "HTTPClient",
    "AllReactionsResponse",
    "GifResponse",
)

import logging

_log = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Set up basic logging for the expressipy package

    Parameters
    ----------
    level : int
        The logging level to use (e.g. logging.DEBUG, logging.INFO)

    Example
    -------
    ```python
    import logging
    from expressipy import setup_logging

    # Enable debug logging to see HTTP requests
    setup_logging(logging.DEBUG)
    ```
    """

    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _log.setLevel(level)
