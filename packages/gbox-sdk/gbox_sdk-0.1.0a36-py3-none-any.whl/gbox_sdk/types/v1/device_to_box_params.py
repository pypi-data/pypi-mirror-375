# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DeviceToBoxParams"]


class DeviceToBoxParams(TypedDict, total=False):
    force: bool
    """
    If true, the device will be forcibly created as a new Box, which will forcibly
    terminate any existing box that is currently using this device. If false, an
    error will be thrown with HTTP 423 status code when the device is already
    occupied by a box.
    """
