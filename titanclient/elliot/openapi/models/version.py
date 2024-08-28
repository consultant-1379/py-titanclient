from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Version")


@_attrs_define
class Version:
    """
    Attributes:
        commit (Union[Unset, str]):  Example: e08c782574351f7d167ef7bed81d1eaca38826b1.
        version (Union[Unset, str]):  Example: 1.1.0.
    """

    commit: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        commit = self.commit

        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if commit is not UNSET:
            field_dict["commit"] = commit
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        commit = d.pop("commit", UNSET)

        version = d.pop("version", UNSET)

        version = cls(
            commit=commit,
            version=version,
        )

        version.additional_properties = d
        return version

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
