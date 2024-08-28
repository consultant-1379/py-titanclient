from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.user import User
from ...types import Response


def _get_kwargs(
    uid: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/user/{uid}".format(
            uid=uid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[User]:
    if response.status_code == HTTPStatus.OK:
        response_200 = User.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[User]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    uid: int,
    *,
    client: AuthenticatedClient,
) -> Response[User]:
    """Get user

    Args:
        uid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[User]
    """

    kwargs = _get_kwargs(
        uid=uid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    uid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[User]:
    """Get user

    Args:
        uid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        User
    """

    return sync_detailed(
        uid=uid,
        client=client,
    ).parsed


async def asyncio_detailed(
    uid: int,
    *,
    client: AuthenticatedClient,
) -> Response[User]:
    """Get user

    Args:
        uid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[User]
    """

    kwargs = _get_kwargs(
        uid=uid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    uid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[User]:
    """Get user

    Args:
        uid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        User
    """

    return (
        await asyncio_detailed(
            uid=uid,
            client=client,
        )
    ).parsed
