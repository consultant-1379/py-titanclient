from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.runtime_status_status import RuntimeStatusStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="RuntimeStatus")


@_attrs_define
class RuntimeStatus:
    """
    Attributes:
        hid (Union[Unset, int]):  Example: 1.
        status (Union[Unset, RuntimeStatusStatus]):  Default: RuntimeStatusStatus.UP.
    """

    hid: Union[Unset, int] = UNSET
    status: Union[Unset, RuntimeStatusStatus] = RuntimeStatusStatus.UP
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hid = self.hid

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hid is not UNSET:
            field_dict["hid"] = hid
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hid = d.pop("hid", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, RuntimeStatusStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = RuntimeStatusStatus(_status)

        runtime_status = cls(
            hid=hid,
            status=status,
        )

        runtime_status.additional_properties = d
        return runtime_status

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
