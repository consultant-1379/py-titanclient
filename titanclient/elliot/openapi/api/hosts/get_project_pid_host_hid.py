from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.host import Host
from ...types import Response


def _get_kwargs(
    pid: int,
    hid: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/project/{pid}/host/{hid}".format(
            pid=pid,
            hid=hid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Host]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Host.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Host]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pid: int,
    hid: int,
    *,
    client: AuthenticatedClient,
) -> Response[Host]:
    """Get host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Host]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pid: int,
    hid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Host]:
    """Get host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Host
    """

    return sync_detailed(
        pid=pid,
        hid=hid,
        client=client,
    ).parsed


async def asyncio_detailed(
    pid: int,
    hid: int,
    *,
    client: AuthenticatedClient,
) -> Response[Host]:
    """Get host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Host]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pid: int,
    hid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Host]:
    """Get host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Host
    """

    return (
        await asyncio_detailed(
            pid=pid,
            hid=hid,
            client=client,
        )
    ).parsed
