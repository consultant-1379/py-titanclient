from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.log_status import LogStatus


T = TypeVar("T", bound="Log")


@_attrs_define
class Log:
    """
    Attributes:
        hid (Union[Unset, int]):
        hostname (Union[Unset, str]):
        id (Union[Unset, str]):
        name (Union[Unset, str]):
        path (Union[Unset, str]):
        runtime (Union[Unset, int]):
        status (Union[Unset, LogStatus]):
    """

    hid: Union[Unset, int] = UNSET
    hostname: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    path: Union[Unset, str] = UNSET
    runtime: Union[Unset, int] = UNSET
    status: Union[Unset, "LogStatus"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hid = self.hid

        hostname = self.hostname

        id = self.id

        name = self.name

        path = self.path

        runtime = self.runtime

        status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hid is not UNSET:
            field_dict["hid"] = hid
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if path is not UNSET:
            field_dict["path"] = path
        if runtime is not UNSET:
            field_dict["runtime"] = runtime
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.log_status import LogStatus

        d = src_dict.copy()
        hid = d.pop("hid", UNSET)

        hostname = d.pop("hostname", UNSET)

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        path = d.pop("path", UNSET)

        runtime = d.pop("runtime", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, LogStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = LogStatus.from_dict(_status)

        log = cls(
            hid=hid,
            hostname=hostname,
            id=id,
            name=name,
            path=path,
            runtime=runtime,
            status=status,
        )

        log.additional_properties = d
        return log

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
