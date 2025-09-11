# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["ActionScreenshotOptions"]


class ActionScreenshotOptions(BaseModel):
    delay: Optional[str] = None
    """Delay after performing the action, before taking the final screenshot.

    Execution flow:

    1. Take screenshot before action
    2. Perform the action
    3. Wait for screenshotDelay (this parameter)
    4. Take screenshot after action

    Example: '500ms' means wait 500ms after the action before capturing the final
    screenshot.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
    """

    output_format: Optional[Literal["base64", "storageKey"]] = FieldInfo(alias="outputFormat", default=None)
    """Type of the URI. default is base64."""

    phases: Optional[List[Literal["before", "after", "trace"]]] = None
    """Specify which screenshot phases to capture.

    Available options:

    - before: Screenshot before the action
    - after: Screenshot after the action
    - trace: Screenshot with operation trace

    Default captures all three phases. Can specify one or multiple in an array. If
    empty array is provided, no screenshots will be taken.
    """

    presigned_expires_in: Optional[str] = FieldInfo(alias="presignedExpiresIn", default=None)
    """Presigned url expires in. Only takes effect when outputFormat is storageKey.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """
