# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["ProxySetParams", "Auth"]


class ProxySetParams(TypedDict, total=False):
    host: Required[str]
    """The host address of the proxy server"""

    port: Required[float]
    """The port number of the proxy server"""

    auth: Auth
    """Box Proxy Auth"""

    excludes: SequenceNotStr[str]
    """List of IP addresses and domains that should bypass the proxy.

    These addresses will be accessed directly without going through the proxy
    server. Default is ['127.0.0.1', 'localhost']
    """

    pac_url: Annotated[str, PropertyInfo(alias="pacUrl")]
    """PAC (Proxy Auto-Configuration) URL."""


class Auth(TypedDict, total=False):
    password: Required[str]
    """Password for the proxy"""

    username: Required[str]
    """Username for the proxy"""
