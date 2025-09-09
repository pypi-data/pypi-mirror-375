# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["ProxySetResponse", "Auth"]


class Auth(BaseModel):
    password: str
    """Password for the proxy"""

    username: str
    """Username for the proxy"""


class ProxySetResponse(BaseModel):
    host: str
    """The host address of the proxy server"""

    port: float
    """The port number of the proxy server"""

    auth: Optional[Auth] = None
    """Box Proxy Auth"""

    excludes: Optional[List[str]] = None
    """List of IP addresses and domains that should bypass the proxy.

    These addresses will be accessed directly without going through the proxy
    server. Default is ['127.0.0.1', 'localhost']
    """

    pac_url: Optional[str] = FieldInfo(alias="pacUrl", default=None)
    """PAC (Proxy Auto-Configuration) URL."""
