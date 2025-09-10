from typing_extensions import List, Union

from gbox_sdk._types import NOT_GIVEN, NotGiven
from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.proxy_set_params import Auth
from gbox_sdk.types.v1.boxes.proxy_get_response import ProxyGetResponse
from gbox_sdk.types.v1.boxes.proxy_set_response import ProxySetResponse


class ProxyOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def set(
        self,
        *,
        host: str,
        port: float,
        auth: Union[Auth, NotGiven] = NOT_GIVEN,
        excludes: Union[List[str], NotGiven] = NOT_GIVEN,
        pac_url: Union[str, NotGiven] = NOT_GIVEN,
    ) -> ProxySetResponse:
        """
        Set the proxy for the box

        Args:
          host: The host address of the proxy server

          port: The port number of the proxy server

          auth: Box Proxy Auth

          excludes: List of IP addresses and domains that should bypass the proxy. These addresses
              will be accessed directly without going through the proxy server. Default is
              ['127.0.0.1', 'localhost']

          pac_url: PAC (Proxy Auto-Configuration) URL.

        Returns:
            ProxySetResponse: The response from the proxy set action.

        Example:
            >>> response = myBox.proxy.set(host="127.0.0.1", port=8080)
        """
        return self.client.v1.boxes.proxy.set(
            box_id=self.box_id, host=host, port=port, auth=auth, excludes=excludes, pac_url=pac_url
        )

    def get(self) -> ProxyGetResponse:
        """
        Get the proxy for the box

        Returns:
            ProxyGetResponse: The response from the proxy get action.

        Example:
            >>> response = myBox.proxy.get()
        """
        return self.client.v1.boxes.proxy.get(box_id=self.box_id)

    def clear(self) -> None:
        """
        Clear the proxy for the box

        Example:
            >>> response = myBox.proxy.clear()
        """
        return self.client.v1.boxes.proxy.clear(box_id=self.box_id)
