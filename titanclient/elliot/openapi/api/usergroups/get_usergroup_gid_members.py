from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.usergroup import Usergroup
from ...types import Response


def _get_kwargs(
    gid: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/usergroup/{gid}/members".format(
            gid=gid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["Usergroup"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Usergroup.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["Usergroup"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    gid: int,
    *,
    client: AuthenticatedClient,
) -> Response[List["Usergroup"]]:
    """List users in group

     Admin only

    Args:
        gid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['Usergroup']]
    """

    kwargs = _get_kwargs(
        gid=gid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    gid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[List["Usergroup"]]:
    """List users in group

     Admin only

    Args:
        gid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['Usergroup']
    """

    return sync_detailed(
        gid=gid,
        client=client,
    ).parsed


async def asyncio_detailed(
    gid: int,
    *,
    client: AuthenticatedClient,
) -> Response[List["Usergroup"]]:
    """List users in group

     Admin only

    Args:
        gid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['Usergroup']]
    """

    kwargs = _get_kwargs(
        gid=gid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    gid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[List["Usergroup"]]:
    """List users in group

     Admin only

    Args:
        gid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['Usergroup']
    """

    return (
        await asyncio_detailed(
            gid=gid,
            client=client,
        )
    ).parsed
