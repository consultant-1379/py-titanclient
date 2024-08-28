from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.log import Log
from ...types import Response


def _get_kwargs(
    pid: int,
    hid: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/project/{pid}/host/{hid}/logs".format(
            pid=pid,
            hid=hid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["Log"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Log.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["Log"]]:
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
) -> Response[List["Log"]]:
    """List executions logs on host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['Log']]
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
) -> Optional[List["Log"]]:
    """List executions logs on host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['Log']
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
) -> Response[List["Log"]]:
    """List executions logs on host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['Log']]
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
) -> Optional[List["Log"]]:
    """List executions logs on host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['Log']
    """

    return (
        await asyncio_detailed(
            pid=pid,
            hid=hid,
            client=client,
        )
    ).parsed
