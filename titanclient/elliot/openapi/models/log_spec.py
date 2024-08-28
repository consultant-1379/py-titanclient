from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LogSpec")


@_attrs_define
class LogSpec:
    """
    Attributes:
        hid (Union[Unset, int]):  Example: 1.
        lid (Union[Unset, str]):  Example: d086c2ba959c5a612aa235a3dd696956.
    """

    hid: Union[Unset, int] = UNSET
    lid: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hid = self.hid

        lid = self.lid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hid is not UNSET:
            field_dict["hid"] = hid
        if lid is not UNSET:
            field_dict["lid"] = lid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hid = d.pop("hid", UNSET)

        lid = d.pop("lid", UNSET)

        log_spec = cls(
            hid=hid,
            lid=lid,
        )

        log_spec.additional_properties = d
        return log_spec

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
