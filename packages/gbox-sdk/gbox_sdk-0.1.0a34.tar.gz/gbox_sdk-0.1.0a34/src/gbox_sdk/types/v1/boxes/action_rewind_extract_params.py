# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ActionRewindExtractParams"]


class ActionRewindExtractParams(TypedDict, total=False):
    duration: str
    """How far back in time to rewind for extracting recorded video.

    This specifies the duration to go back from the current moment (e.g., '30s'
    rewinds 30 seconds to get recent recorded activity). Default is 30s, max is 5m.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Maximum allowed: 5m
    """
