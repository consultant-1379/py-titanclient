from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.gpl_scenario_timeline_data_item import GPLScenarioTimelineDataItem


T = TypeVar("T", bound="GPLScenarioTimeline")


@_attrs_define
class GPLScenarioTimeline:
    """
    Attributes:
        data (Union[Unset, List['GPLScenarioTimelineDataItem']]):
        scenario (Union[Unset, str]):
    """

    data: Union[Unset, List["GPLScenarioTimelineDataItem"]] = UNSET
    scenario: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)

        scenario = self.scenario

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if scenario is not UNSET:
            field_dict["scenario"] = scenario

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.gpl_scenario_timeline_data_item import GPLScenarioTimelineDataItem

        d = src_dict.copy()
        data = []
        _data = d.pop("data", UNSET)
        for data_item_data in _data or []:
            data_item = GPLScenarioTimelineDataItem.from_dict(data_item_data)

            data.append(data_item)

        scenario = d.pop("scenario", UNSET)

        gpl_scenario_timeline = cls(
            data=data,
            scenario=scenario,
        )

        gpl_scenario_timeline.additional_properties = d
        return gpl_scenario_timeline

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
