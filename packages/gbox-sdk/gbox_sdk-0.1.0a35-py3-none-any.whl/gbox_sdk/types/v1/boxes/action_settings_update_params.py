# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ActionSettingsUpdateParams"]


class ActionSettingsUpdateParams(TypedDict, total=False):
    scale: Required[float]
    """The scale of the action to be performed.

    Must be greater than 0.1 and less than or equal to 1.

    Notes:

    - Scale does not change the box's actual screen resolution.
    - It affects the size of the output screenshot and the coordinates/distances of
      actions. Coordinates and distances are scaled by this factor. Example: when
      scale = 1, Click({x:100, y:100}); when scale = 0.5, the equivalent position is
      Click({x:50, y:50}).
    """
