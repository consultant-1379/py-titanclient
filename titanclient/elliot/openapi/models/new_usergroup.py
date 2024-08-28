from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.permission import Permission
    from ..models.user import User


T = TypeVar("T", bound="NewUsergroup")


@_attrs_define
class NewUsergroup:
    """
    Attributes:
        members (Union[Unset, List['User']]):
        name (Union[Unset, str]):  Example: usergroup.
        permissions (Union[Unset, List['Permission']]):
    """

    members: Union[Unset, List["User"]] = UNSET
    name: Union[Unset, str] = UNSET
    permissions: Union[Unset, List["Permission"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        members: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()
                members.append(members_item)

        name = self.name

        permissions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = []
            for permissions_item_data in self.permissions:
                permissions_item = permissions_item_data.to_dict()
                permissions.append(permissions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if members is not UNSET:
            field_dict["members"] = members
        if name is not UNSET:
            field_dict["name"] = name
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.permission import Permission
        from ..models.user import User

        d = src_dict.copy()
        members = []
        _members = d.pop("members", UNSET)
        for members_item_data in _members or []:
            members_item = User.from_dict(members_item_data)

            members.append(members_item)

        name = d.pop("name", UNSET)

        permissions = []
        _permissions = d.pop("permissions", UNSET)
        for permissions_item_data in _permissions or []:
            permissions_item = Permission.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        new_usergroup = cls(
            members=members,
            name=name,
            permissions=permissions,
        )

        new_usergroup.additional_properties = d
        return new_usergroup

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
