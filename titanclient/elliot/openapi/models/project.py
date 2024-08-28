from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usergroup import Usergroup


T = TypeVar("T", bound="Project")


@_attrs_define
class Project:
    """
    Attributes:
        id (Union[Unset, int]):  Example: 1.
        name (Union[Unset, str]):  Example: project1.
        usergroups (Union[Unset, List['Usergroup']]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    usergroups: Union[Unset, List["Usergroup"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        usergroups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.usergroups, Unset):
            usergroups = []
            for usergroups_item_data in self.usergroups:
                usergroups_item = usergroups_item_data.to_dict()
                usergroups.append(usergroups_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if usergroups is not UNSET:
            field_dict["usergroups"] = usergroups

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.usergroup import Usergroup

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        usergroups = []
        _usergroups = d.pop("usergroups", UNSET)
        for usergroups_item_data in _usergroups or []:
            usergroups_item = Usergroup.from_dict(usergroups_item_data)

            usergroups.append(usergroups_item)

        project = cls(
            id=id,
            name=name,
            usergroups=usergroups,
        )

        project.additional_properties = d
        return project

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
