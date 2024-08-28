from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.log_stat import LogStat
from ...models.log_stat_query import LogStatQuery
from ...types import Response


def _get_kwargs(
    pid: int,
    *,
    body: LogStatQuery,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/project/{pid}/batch/gpl".format(
            pid=pid,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["LogStat"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = LogStat.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["LogStat"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pid: int,
    *,
    client: AuthenticatedClient,
    body: LogStatQuery,
) -> Response[List["LogStat"]]:
    """Get GPL statistics from multiple hosts

    Args:
        pid (int):  Example: 1.
        body (LogStatQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['LogStat']]
    """

    kwargs = _get_kwargs(
        pid=pid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pid: int,
    *,
    client: AuthenticatedClient,
    body: LogStatQuery,
) -> Optional[List["LogStat"]]:
    """Get GPL statistics from multiple hosts

    Args:
        pid (int):  Example: 1.
        body (LogStatQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['LogStat']
    """

    return sync_detailed(
        pid=pid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    pid: int,
    *,
    client: AuthenticatedClient,
    body: LogStatQuery,
) -> Response[List["LogStat"]]:
    """Get GPL statistics from multiple hosts

    Args:
        pid (int):  Example: 1.
        body (LogStatQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['LogStat']]
    """

    kwargs = _get_kwargs(
        pid=pid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pid: int,
    *,
    client: AuthenticatedClient,
    body: LogStatQuery,
) -> Optional[List["LogStat"]]:
    """Get GPL statistics from multiple hosts

    Args:
        pid (int):  Example: 1.
        body (LogStatQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['LogStat']
    """

    return (
        await asyncio_detailed(
            pid=pid,
            client=client,
            body=body,
        )
    ).parsed
