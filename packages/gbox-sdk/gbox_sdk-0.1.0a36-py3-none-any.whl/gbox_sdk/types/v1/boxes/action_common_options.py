# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import TypeAlias

from ...._models import BaseModel
from .action_screenshot_options import ActionScreenshotOptions

__all__ = ["ActionCommonOptions", "Screenshot"]

Screenshot: TypeAlias = Union[ActionScreenshotOptions, bool]


class ActionCommonOptions(BaseModel):
    screenshot: Optional[Screenshot] = None
    """Screenshot options.

    Can be a boolean to enable/disable screenshots, or an object to configure
    screenshot options.
    """
