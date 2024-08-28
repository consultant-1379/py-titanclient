from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.gpl_timeline import GPLTimeline
from ...models.gpl_timeline_query import GPLTimelineQuery
from ...types import Response


def _get_kwargs(
    pid: int,
    hid: int,
    lid: str,
    *,
    body: GPLTimelineQuery,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/project/{pid}/host/{hid}/log/{lid}/gpl/timeline".format(
            pid=pid,
            hid=hid,
            lid=lid,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GPLTimeline]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GPLTimeline.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GPLTimeline]:
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
    body: GPLTimelineQuery,
) -> Response[GPLTimeline]:
    """Get GPL timeline from host log

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.
        body (GPLTimelineQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GPLTimeline]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
        lid=lid,
        body=body,
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
    body: GPLTimelineQuery,
) -> Optional[GPLTimeline]:
    """Get GPL timeline from host log

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.
        body (GPLTimelineQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GPLTimeline
    """

    return sync_detailed(
        pid=pid,
        hid=hid,
        lid=lid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    pid: int,
    hid: int,
    lid: str,
    *,
    client: AuthenticatedClient,
    body: GPLTimelineQuery,
) -> Response[GPLTimeline]:
    """Get GPL timeline from host log

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.
        body (GPLTimelineQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GPLTimeline]
    """

    kwargs = _get_kwargs(
        pid=pid,
        hid=hid,
        lid=lid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pid: int,
    hid: int,
    lid: str,
    *,
    client: AuthenticatedClient,
    body: GPLTimelineQuery,
) -> Optional[GPLTimeline]:
    """Get GPL timeline from host log

    Args:
        pid (int):  Example: 1.
        hid (int):  Example: 1.
        lid (str):  Example: 04c8514e-e560-962a-4e70-7f6234b9dd31.
        body (GPLTimelineQuery):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GPLTimeline
    """

    return (
        await asyncio_detailed(
            pid=pid,
            hid=hid,
            lid=lid,
            client=client,
            body=body,
        )
    ).parsed
