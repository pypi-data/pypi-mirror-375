# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from .dir import Dir
from .file import File
from ...._models import BaseModel

__all__ = ["FListResponse", "Data"]

Data: TypeAlias = Union[File, Dir]


class FListResponse(BaseModel):
    data: List[Data]
    """Array of files and directories"""
