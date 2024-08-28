from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PasswordChange")


@_attrs_define
class PasswordChange:
    """
    Attributes:
        new (Union[Unset, str]):  Example: newpassword.
        old (Union[Unset, str]):  Example: oldpassword.
    """

    new: Union[Unset, str] = UNSET
    old: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new = self.new

        old = self.old

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if new is not UNSET:
            field_dict["new"] = new
        if old is not UNSET:
            field_dict["old"] = old

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        new = d.pop("new", UNSET)

        old = d.pop("old", UNSET)

        password_change = cls(
            new=new,
            old=old,
        )

        password_change.additional_properties = d
        return password_change

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
