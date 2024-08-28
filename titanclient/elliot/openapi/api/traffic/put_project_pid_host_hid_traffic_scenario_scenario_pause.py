from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import Response


def _get_kwargs(
    pid: int,
    hid: int,
    scenario: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": "/project/{pid}/host/{hid}/traffic/scenario/{scenario}/pause".format(
            pid=pid,
            hid=hid,
            scenario=scenario,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Any]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pid: int,
    hid: int,
    scenario: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any]:
    """Pause scenario on host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        scenario (str):  Example: 0011PsPs_A.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
        scenario=scenario,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    pid: int,
    hid: int,
    scenario: str,
    *,
    client: AuthenticatedClient,
) -> Response[Any]:
    """Pause scenario on host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        scenario (str):  Example: 0011PsPs_A.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
        scenario=scenario,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
