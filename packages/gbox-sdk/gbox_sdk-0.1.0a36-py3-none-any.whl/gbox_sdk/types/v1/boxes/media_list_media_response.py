# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from ...._models import BaseModel
from .media_photo import MediaPhoto
from .media_video import MediaVideo

__all__ = ["MediaListMediaResponse", "Data"]

Data: TypeAlias = Union[MediaPhoto, MediaVideo]


class MediaListMediaResponse(BaseModel):
    data: List[Data]
    """List of media files (photos and videos) in the album"""
