# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from .device_info import DeviceInfo

__all__ = ["GetDeviceListResponse"]


class GetDeviceListResponse(BaseModel):
    data: List[DeviceInfo]
    """List of devices"""

    message: str
    """Response message"""

    total: float
    """Total number of devices"""
