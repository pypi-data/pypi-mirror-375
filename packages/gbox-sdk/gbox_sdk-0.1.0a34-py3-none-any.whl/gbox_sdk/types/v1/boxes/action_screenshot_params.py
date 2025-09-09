# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ActionScreenshotParams", "Clip"]


class ActionScreenshotParams(TypedDict, total=False):
    clip: Clip
    """Clipping region for screenshot capture"""

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """Type of the URI. default is base64."""

    presigned_expires_in: Annotated[str, PropertyInfo(alias="presignedExpiresIn")]
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    save_to_album: Annotated[bool, PropertyInfo(alias="saveToAlbum")]
    """Whether to save the screenshot to the device screenshot album"""


class Clip(TypedDict, total=False):
    height: Required[float]
    """Height of the clip"""

    width: Required[float]
    """Width of the clip"""

    x: Required[float]
    """X coordinate of the clip"""

    y: Required[float]
    """Y coordinate of the clip"""
