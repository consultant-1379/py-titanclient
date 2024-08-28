from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.gpl_scenario_timeline import GPLScenarioTimeline


T = TypeVar("T", bound="GPLTimeline")


@_attrs_define
class GPLTimeline:
    """
    Attributes:
        from_ (Union[Unset, int]):  Example: 1.
        items (Union[Unset, List['GPLScenarioTimeline']]):
        rate (Union[Unset, int]):  Example: 50.
        to (Union[Unset, int]):  Example: 1.
    """

    from_: Union[Unset, int] = UNSET
    items: Union[Unset, List["GPLScenarioTimeline"]] = UNSET
    rate: Union[Unset, int] = UNSET
    to: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_ = self.from_

        items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)

        rate = self.rate

        to = self.to

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_ is not UNSET:
            field_dict["from"] = from_
        if items is not UNSET:
            field_dict["items"] = items
        if rate is not UNSET:
            field_dict["rate"] = rate
        if to is not UNSET:
            field_dict["to"] = to

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.gpl_scenario_timeline import GPLScenarioTimeline

        d = src_dict.copy()
        from_ = d.pop("from", UNSET)

        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in _items or []:
            items_item = GPLScenarioTimeline.from_dict(items_item_data)

            items.append(items_item)

        rate = d.pop("rate", UNSET)

        to = d.pop("to", UNSET)

        gpl_timeline = cls(
            from_=from_,
            items=items,
            rate=rate,
            to=to,
        )

        gpl_timeline.additional_properties = d
        return gpl_timeline

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
