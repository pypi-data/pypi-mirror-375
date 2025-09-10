# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel
from .android_pkg import AndroidPkg

__all__ = ["AndroidListPkgResponse"]


class AndroidListPkgResponse(BaseModel):
    data: List[AndroidPkg]
    """Android pkg list"""
