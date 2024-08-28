from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.log import Log
from ...types import Response


def _get_kwargs(
    pid: int,
    hid: int,
    lid: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/project/{pid}/host/{hid}/log/{lid}".format(
            pid=pid,
            hid=hid,
            lid=lid,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Log]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Log.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Log]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pid: int,
    hid: int,
    lid: str,
    *,
    client: AuthenticatedClient,
) -> Response[Log]:
    """Get execution log from host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Log]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
        lid=lid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pid: int,
    hid: int,
    lid: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Log]:
    """Get execution log from host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Log
    """

    return sync_detailed(
        pid=pid,
        hid=hid,
        lid=lid,
        client=client,
    ).parsed


async def asyncio_detailed(
    pid: int,
    hid: int,
    lid: str,
    *,
    client: AuthenticatedClient,
) -> Response[Log]:
    """Get execution log from host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Log]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
        lid=lid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pid: int,
    hid: int,
    lid: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Log]:
    """Get execution log from host

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Log
    """

    return (
        await asyncio_detailed(
            pid=pid,
            hid=hid,
            lid=lid,
            client=client,
        )
    ).parsed
