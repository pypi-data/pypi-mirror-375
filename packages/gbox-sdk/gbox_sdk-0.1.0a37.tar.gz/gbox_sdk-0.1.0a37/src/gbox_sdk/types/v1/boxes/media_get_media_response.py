# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import TypeAlias

from .media_photo import MediaPhoto
from .media_video import MediaVideo

__all__ = ["MediaGetMediaResponse"]

MediaGetMediaResponse: TypeAlias = Union[MediaPhoto, MediaVideo]
