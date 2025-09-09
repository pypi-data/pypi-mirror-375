"""Module that implements a client abstraction that makes it easy to communicate with the Dapla Pseudo Service REST API."""

import asyncio
import os
import typing as t

import google.auth.transport.requests
import google.oauth2.id_token
from aiohttp import ClientResponse
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector
from aiohttp_retry import ExponentialRetry
from aiohttp_retry import RetryClient
from dapla_auth_client import AuthClient
from ulid import ULID

from whodat.constants import Env
from whodat.model import WhodatRequest
from whodat.model import WhodatResponse


class WhodatClient:
    """Client for interacting with the Dapla Pseudo Service REST API."""

    def __init__(
        self,
        whodat_service_url: str | None = None,
        auth_token: str | None = None,
    ) -> None:
        """Constructor for WhodatClient.

        Args:
            whodat_service_url (str | None, optional): Base URL for Whodat Service
            auth_token (str | None, optional): Static auth token
        """
        self.whodat_service_url = whodat_service_url
        self.static_auth_token = auth_token

    def __auth_token(self) -> str:
        if os.environ.get("DAPLA_REGION") == "CLOUD_RUN":
            audience = os.environ["WHODAT_SERVICE_URL"]
            auth_req = google.auth.transport.requests.Request()  # type: ignore[no-untyped-call]
            token = t.cast(
                str,
                google.oauth2.id_token.fetch_id_token(auth_req, audience),  # type: ignore[no-untyped-call]
            )
            return token
        else:
            return (
                str(AuthClient.fetch_personal_token())
                if self.static_auth_token is None
                else str(self.static_auth_token)
            )

    async def post_to_field_endpoint(
        self,
        path: str,
        timeout: int,
        whodat_requests: list[list[WhodatRequest]],
    ) -> list[tuple[WhodatResponse, int]]:
        """Post a request to the Pseudo Service field endpoint.

        Args:
            path (str): Full URL to the endpoint
            timeout (int): Request timeout
            whodat_requests: list[list[WhodatRequest]] Whodat requests, with each inner list representing the requests for a single row.

        Returns:
            list[tuple[WhodatResponse, int]]: A list of tuple of (field_name, data, metadata)
        """

        async def _post(
            client: RetryClient,
            path: str,
            timeout: int,
            requests: list[WhodatRequest],
            correlation_id: str,
        ) -> tuple[WhodatResponse, int]:
            for num_request, request in enumerate(requests, start=1):
                async with client.post(
                    url=f"{self.whodat_service_url}/{path}",
                    headers={
                        "Authorization": f"Bearer {self.__auth_token()}",
                        "Content-Type": "application/json",
                        "X-Correlation-Id": correlation_id,
                    },
                    json=request.model_dump(),
                    timeout=timeout,
                ) as response:
                    await WhodatClient._handle_response_error(response)
                    response_json = await response.json()
                    found_personal_ids = response_json.get("foedselsEllerDNummer", [])
                    if len(found_personal_ids) == 1:  # Early return if unique ID found
                        return (
                            WhodatResponse.model_validate(
                                {"found_personal_ids": found_personal_ids}
                            ),
                            num_request,
                        )

            return (
                WhodatResponse.model_validate(  # Late return if all attempts exhausted
                    {"found_personal_ids": found_personal_ids}
                ),
                num_request,
            )

        aio_session = ClientSession(
            connector=TCPConnector(limit=200, force_close=True),
            timeout=ClientTimeout(total=60 * 60 * 24),
        )
        async with RetryClient(
            client_session=aio_session,
            retry_options=ExponentialRetry(
                attempts=5,
                start_timeout=0.1,
                max_timeout=30,
                factor=6,
                statuses={
                    400,
                }.union(
                    set(range(500, 600))
                ),  # Retry all 5xx errors and 400 Bad Request
            ),
        ) as client:
            results = await asyncio.gather(
                *[
                    _post(
                        client=client,
                        path=path,
                        timeout=timeout,
                        requests=reqs,
                        correlation_id=WhodatClient._generate_new_correlation_id(),
                    )
                    for reqs in whodat_requests
                ]
            )
        await asyncio.sleep(0.1)  # Allow time for sockets to close
        await aio_session.close()

        return results

    @staticmethod
    async def _handle_response_error(response: ClientResponse) -> None:
        """Report error messages in response object."""
        match response.status:
            case status if status in range(200, 300):
                pass
            case _:
                print(response.headers)
                print(await response.text())
                response.raise_for_status()

    @staticmethod
    def _generate_new_correlation_id() -> str:
        return str(ULID())


def _client() -> WhodatClient:
    return WhodatClient(
        whodat_service_url=os.getenv(Env.WHODAT_SERVICE_URL),
        auth_token=os.getenv(Env.WHODAT_SERVICE_AUTH_TOKEN),
    )
