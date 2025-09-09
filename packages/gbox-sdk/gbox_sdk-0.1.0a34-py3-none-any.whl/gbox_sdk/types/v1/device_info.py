# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DeviceInfo"]


class DeviceInfo(BaseModel):
    device_id: str = FieldInfo(alias="deviceId")
    """Device ID"""

    enable: str
    """Device enable status"""

    is_idle: bool = FieldInfo(alias="isIdle")
    """Whether device is idle"""

    product_model: str = FieldInfo(alias="productModel")
    """Product model from ro.product.model"""

    provider_id: str = FieldInfo(alias="providerId")
    """Provider ID"""

    provider_type: str = FieldInfo(alias="providerType")
    """Provider type"""

    status: str
    """Device status"""
