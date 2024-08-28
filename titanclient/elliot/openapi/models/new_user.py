from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NewUser")


@_attrs_define
class NewUser:
    """
    Attributes:
        name (Union[Unset, str]):  Example: Administrator.
        password (Union[Unset, str]):  Example: password.
        roles (Union[Unset, str]):  Example: admin,user.
        username (Union[Unset, str]):  Example: admin.
    """

    name: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    roles: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        password = self.password

        roles = self.roles

        username = self.username

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if password is not UNSET:
            field_dict["password"] = password
        if roles is not UNSET:
            field_dict["roles"] = roles
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        password = d.pop("password", UNSET)

        roles = d.pop("roles", UNSET)

        username = d.pop("username", UNSET)

        new_user = cls(
            name=name,
            password=password,
            roles=roles,
            username=username,
        )

        new_user.additional_properties = d
        return new_user

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
