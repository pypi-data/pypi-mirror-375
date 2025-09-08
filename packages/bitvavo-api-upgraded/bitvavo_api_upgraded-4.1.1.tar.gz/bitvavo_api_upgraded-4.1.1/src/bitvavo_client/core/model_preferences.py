"""Model preference enum for API endpoints."""

from __future__ import annotations

import sys
from enum import Enum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        """Compatibility StrEnum for Python < 3.11."""


class ModelPreference(StrEnum):
    """Enumeration of available model preferences for API responses.

    This enum allows users to specify their preferred response format across
    all API methods without having to pass model parameters to each call.
    """

    # Return raw Python data structures (dict/list)
    RAW = "raw"

    # Return Polars DataFrame (requires schema)
    DATAFRAME = "dataframe"

    # Return appropriate Pydantic model for each endpoint
    PYDANTIC = "pydantic"

    # Let each method use its own default (legacy behavior)
    AUTO = "auto"
