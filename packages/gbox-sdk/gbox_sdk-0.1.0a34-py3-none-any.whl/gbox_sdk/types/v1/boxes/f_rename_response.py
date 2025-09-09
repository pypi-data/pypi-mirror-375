# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import TypeAlias

from .dir import Dir
from .file import File

__all__ = ["FRenameResponse"]

FRenameResponse: TypeAlias = Union[File, Dir]
