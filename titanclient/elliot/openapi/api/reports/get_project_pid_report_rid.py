from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.report import Report
from ...types import Response


def _get_kwargs(
    pid: int,
    rid: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/project/{pid}/report/{rid}".format(
            pid=pid,
            rid=rid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Report]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Report.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Report]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pid: int,
    rid: int,
    *,
    client: AuthenticatedClient,
) -> Response[Report]:
    """Get report

    Args:
        pid (int):  Example: 1.
        rid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Report]
    """

    kwargs = _get_kwargs(
        pid=pid,
        rid=rid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pid: int,
    rid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Report]:
    """Get report

    Args:
        pid (int):  Example: 1.
        rid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Report
    """

    return sync_detailed(
        pid=pid,
        rid=rid,
        client=client,
    ).parsed


async def asyncio_detailed(
    pid: int,
    rid: int,
    *,
    client: AuthenticatedClient,
) -> Response[Report]:
    """Get report

    Args:
        pid (int):  Example: 1.
        rid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Report]
    """

    kwargs = _get_kwargs(
        pid=pid,
        rid=rid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pid: int,
    rid: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Report]:
    """Get report

    Args:
        pid (int):  Example: 1.
        rid (int):  Example: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Report
    """

    return (
        await asyncio_detailed(
            pid=pid,
            rid=rid,
            client=client,
        )
    ).parsed
