# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["MediaVideo"]


class MediaVideo(BaseModel):
    last_modified: datetime = FieldInfo(alias="lastModified")
    """Last modified time of the video"""

    mime_type: str = FieldInfo(alias="mimeType")
    """MIME type of the video"""

    name: str
    """Name of the video"""

    path: str
    """Full path to the video in the box"""

    size: str
    """Size of the video"""

    type: Literal["video"]
    """Video type indicator"""
