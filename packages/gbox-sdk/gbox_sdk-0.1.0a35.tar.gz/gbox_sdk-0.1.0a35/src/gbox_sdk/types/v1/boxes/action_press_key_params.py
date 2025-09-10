# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .action_common_options_param import ActionCommonOptionsParam

__all__ = ["ActionPressKeyParams"]

KeysType = List[
    Literal[
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "f1",
        "f2",
        "f3",
        "f4",
        "f5",
        "f6",
        "f7",
        "f8",
        "f9",
        "f10",
        "f11",
        "f12",
        "control",
        "alt",
        "shift",
        "meta",
        "win",
        "cmd",
        "option",
        "arrowUp",
        "arrowDown",
        "arrowLeft",
        "arrowRight",
        "home",
        "end",
        "pageUp",
        "pageDown",
        "enter",
        "space",
        "tab",
        "escape",
        "backspace",
        "delete",
        "insert",
        "capsLock",
        "numLock",
        "scrollLock",
        "pause",
        "printScreen",
        ";",
        "=",
        ",",
        "-",
        ".",
        "/",
        "`",
        "[",
        "\\",
        "]",
        "'",
        "numpad0",
        "numpad1",
        "numpad2",
        "numpad3",
        "numpad4",
        "numpad5",
        "numpad6",
        "numpad7",
        "numpad8",
        "numpad9",
        "numpadAdd",
        "numpadSubtract",
        "numpadMultiply",
        "numpadDivide",
        "numpadDecimal",
        "numpadEnter",
        "numpadEqual",
        "volumeUp",
        "volumeDown",
        "volumeMute",
        "mediaPlayPause",
        "mediaStop",
        "mediaNextTrack",
        "mediaPreviousTrack",
    ]
]


class ActionPressKeyParams(TypedDict, total=False):
    keys: Required[KeysType]
    """This is an array of keyboard keys to press.

    Supports cross-platform compatibility.
    """

    combination: bool
    """Whether to press keys as combination (simultaneously) or sequentially.

    When true, all keys are pressed together as a shortcut (e.g., Ctrl+C). When
    false, keys are pressed one by one in sequence.
    """

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """⚠️ DEPRECATED: Use `options.screenshot.phases` instead.

    This field will be ignored when `options.screenshot` is provided. Whether to
    include screenshots in the action response. If false, the screenshot object will
    still be returned but with empty URIs. Default is false.
    """

    options: ActionCommonOptionsParam
    """Action common options"""

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """⚠️ DEPRECATED: Use `options.screenshot.outputFormat` instead.

    Type of the URI. default is base64. This field will be ignored when
    `options.screenshot` is provided.
    """

    presigned_expires_in: Annotated[str, PropertyInfo(alias="presignedExpiresIn")]
    """⚠️ DEPRECATED: Use `options.screenshot.presignedExpiresIn` instead.

    Presigned url expires in. Only takes effect when outputFormat is storageKey.
    This field will be ignored when `options.screenshot` is provided.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 30m
    """

    screenshot_delay: Annotated[str, PropertyInfo(alias="screenshotDelay")]
    """⚠️ DEPRECATED: Use `options.screenshot.delay` instead.

    This field will be ignored when `options.screenshot` is provided.

    Delay after performing the action, before taking the final screenshot.

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
