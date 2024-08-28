from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.docs import Docs
from ...types import Response


def _get_kwargs(
    page: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/docs/{page}".format(
            page=page,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Docs]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Docs.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Docs]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    page: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Docs]:
    """Load documentation page

    Args:
        page (str):  Example: logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Docs]
    """

    kwargs = _get_kwargs(
        page=page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    page: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Docs]:
    """Load documentation page

    Args:
        page (str):  Example: logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Docs
    """

    return sync_detailed(
        page=page,
        client=client,
    ).parsed


async def asyncio_detailed(
    page: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Docs]:
    """Load documentation page

    Args:
        page (str):  Example: logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Docs]
    """

    kwargs = _get_kwargs(
        page=page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    page: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Docs]:
    """Load documentation page

    Args:
        page (str):  Example: logs.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Docs
    """

    return (
        await asyncio_detailed(
            page=page,
            client=client,
        )
    ).parsed
