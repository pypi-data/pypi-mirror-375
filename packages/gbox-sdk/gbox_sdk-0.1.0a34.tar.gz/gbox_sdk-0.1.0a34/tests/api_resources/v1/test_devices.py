# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gbox_sdk import GboxClient, AsyncGboxClient
from tests.utils import assert_matches_type
from gbox_sdk.types.v1 import DeviceInfo, GetDeviceListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDevices:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: GboxClient) -> None:
        device = client.v1.devices.list()
        assert_matches_type(GetDeviceListResponse, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: GboxClient) -> None:
        response = client.v1.devices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        device = response.parse()
        assert_matches_type(GetDeviceListResponse, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: GboxClient) -> None:
        with client.v1.devices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            device = response.parse()
            assert_matches_type(GetDeviceListResponse, device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: GboxClient) -> None:
        device = client.v1.devices.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(DeviceInfo, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: GboxClient) -> None:
        response = client.v1.devices.with_raw_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        device = response.parse()
        assert_matches_type(DeviceInfo, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: GboxClient) -> None:
        with client.v1.devices.with_streaming_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            device = response.parse()
            assert_matches_type(DeviceInfo, device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `device_id` but received ''"):
            client.v1.devices.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_to_box(self, client: GboxClient) -> None:
        device = client.v1.devices.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(str, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_to_box_with_all_params(self, client: GboxClient) -> None:
        device = client.v1.devices.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            force=True,
        )
        assert_matches_type(str, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_to_box(self, client: GboxClient) -> None:
        response = client.v1.devices.with_raw_response.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        device = response.parse()
        assert_matches_type(str, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_to_box(self, client: GboxClient) -> None:
        with client.v1.devices.with_streaming_response.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            device = response.parse()
            assert_matches_type(str, device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_to_box(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `device_id` but received ''"):
            client.v1.devices.with_raw_response.to_box(
                device_id="",
            )


class TestAsyncDevices:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncGboxClient) -> None:
        device = await async_client.v1.devices.list()
        assert_matches_type(GetDeviceListResponse, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.devices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        device = await response.parse()
        assert_matches_type(GetDeviceListResponse, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.devices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            device = await response.parse()
            assert_matches_type(GetDeviceListResponse, device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncGboxClient) -> None:
        device = await async_client.v1.devices.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(DeviceInfo, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.devices.with_raw_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        device = await response.parse()
        assert_matches_type(DeviceInfo, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.devices.with_streaming_response.get(
            "c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            device = await response.parse()
            assert_matches_type(DeviceInfo, device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `device_id` but received ''"):
            await async_client.v1.devices.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_to_box(self, async_client: AsyncGboxClient) -> None:
        device = await async_client.v1.devices.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(str, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_to_box_with_all_params(self, async_client: AsyncGboxClient) -> None:
        device = await async_client.v1.devices.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            force=True,
        )
        assert_matches_type(str, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_to_box(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.devices.with_raw_response.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        device = await response.parse()
        assert_matches_type(str, device, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_to_box(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.devices.with_streaming_response.to_box(
            device_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            device = await response.parse()
            assert_matches_type(str, device, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_to_box(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `device_id` but received ''"):
            await async_client.v1.devices.with_raw_response.to_box(
                device_id="",
            )
