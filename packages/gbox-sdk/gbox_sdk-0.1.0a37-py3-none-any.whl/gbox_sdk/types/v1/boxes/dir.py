# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["Dir"]


class Dir(BaseModel):
    last_modified: datetime = FieldInfo(alias="lastModified")
    """Last modified time of the directory"""

    mode: str
    """Directory metadata"""

    name: str
    """Name of the directory"""

    path: str
    """Full path to the directory in the box"""

    type: Literal["dir"]
    """Directory type indicator"""
