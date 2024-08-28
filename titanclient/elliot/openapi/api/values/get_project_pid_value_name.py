from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_project_pid_value_name_name import GetProjectPidValueNameName
from ...models.value import Value
from ...models.value_dict import ValueDict
from ...types import Response


def _get_kwargs(
    pid: int,
    name: GetProjectPidValueNameName,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/project/{pid}/value/{name}".format(
            pid=pid,
            name=name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union["ValueDict", List["Value"]]]:
    if response.status_code == HTTPStatus.OK:

        def _parse_response_200(data: object) -> Union["ValueDict", List["Value"]]:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                response_200_type_0 = []
                _response_200_type_0 = data
                for componentsschemas_value_list_item_data in _response_200_type_0:
                    componentsschemas_value_list_item = Value.from_dict(
                        componentsschemas_value_list_item_data
                    )

                    response_200_type_0.append(componentsschemas_value_list_item)

                return response_200_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_1 = ValueDict.from_dict(data)

            return response_200_type_1

        response_200 = _parse_response_200(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union["ValueDict", List["Value"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pid: int,
    name: GetProjectPidValueNameName,
    *,
    client: AuthenticatedClient,
) -> Response[Union["ValueDict", List["Value"]]]:
    """Get available value names

     Values are provided by the underlying library `titanclient`.

    Args:
        pid (int):  Example: 1.
        name (GetProjectPidValueNameName):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union['ValueDict', List['Value']]]
    """

    kwargs = _get_kwargs(
        pid=pid,
        name=name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pid: int,
    name: GetProjectPidValueNameName,
    *,
    client: AuthenticatedClient,
) -> Optional[Union["ValueDict", List["Value"]]]:
    """Get available value names

     Values are provided by the underlying library `titanclient`.

    Args:
        pid (int):  Example: 1.
        name (GetProjectPidValueNameName):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union['ValueDict', List['Value']]
    """

    return sync_detailed(
        pid=pid,
        name=name,
        client=client,
    ).parsed


async def asyncio_detailed(
    pid: int,
    name: GetProjectPidValueNameName,
    *,
    client: AuthenticatedClient,
) -> Response[Union["ValueDict", List["Value"]]]:
    """Get available value names

     Values are provided by the underlying library `titanclient`.

    Args:
        pid (int):  Example: 1.
        name (GetProjectPidValueNameName):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union['ValueDict', List['Value']]]
    """

    kwargs = _get_kwargs(
        pid=pid,
        name=name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pid: int,
    name: GetProjectPidValueNameName,
    *,
    client: AuthenticatedClient,
) -> Optional[Union["ValueDict", List["Value"]]]:
    """Get available value names

     Values are provided by the underlying library `titanclient`.

    Args:
        pid (int):  Example: 1.
        name (GetProjectPidValueNameName):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union['ValueDict', List['Value']]
    """

    return (
        await asyncio_detailed(
            pid=pid,
            name=name,
            client=client,
        )
    ).parsed
