# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel
from .media_album import MediaAlbum

__all__ = ["MediaListAlbumsResponse"]


class MediaListAlbumsResponse(BaseModel):
    data: List[MediaAlbum]
    """List of albums"""
