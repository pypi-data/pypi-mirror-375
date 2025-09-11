# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ...._types import FileTypes, SequenceNotStr

__all__ = ["MediaCreateAlbumParams"]


class MediaCreateAlbumParams(TypedDict, total=False):
    name: Required[str]
    """Name of the album to create"""

    media: SequenceNotStr[FileTypes]
    """Media files to include in the album (max size: 512MB per file)"""
