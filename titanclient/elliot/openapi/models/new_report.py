from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.log_spec import LogSpec
    from ..models.new_report_values import NewReportValues


T = TypeVar("T", bound="NewReport")


@_attrs_define
class NewReport:
    """
    Attributes:
        description (Union[Unset, str]):  Example: test description.
        logs (Union[Unset, List['LogSpec']]):
        merged (Union[Unset, bool]):  Example: True.
        name (Union[Unset, str]):  Example: test report.
        summarized (Union[Unset, bool]):  Example: True.
        timestamp (Union[Unset, int]):  Example: 1656403729.
        values (Union[Unset, NewReportValues]):
    """

    description: Union[Unset, str] = UNSET
    logs: Union[Unset, List["LogSpec"]] = UNSET
    merged: Union[Unset, bool] = UNSET
    name: Union[Unset, str] = UNSET
    summarized: Union[Unset, bool] = UNSET
    timestamp: Union[Unset, int] = UNSET
    values: Union[Unset, "NewReportValues"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        description = self.description

        logs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.logs, Unset):
            logs = []
            for logs_item_data in self.logs:
                logs_item = logs_item_data.to_dict()
                logs.append(logs_item)

        merged = self.merged

        name = self.name

        summarized = self.summarized

        timestamp = self.timestamp

        values: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.values, Unset):
            values = self.values.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if logs is not UNSET:
            field_dict["logs"] = logs
        if merged is not UNSET:
            field_dict["merged"] = merged
        if name is not UNSET:
            field_dict["name"] = name
        if summarized is not UNSET:
            field_dict["summarized"] = summarized
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.log_spec import LogSpec
        from ..models.new_report_values import NewReportValues

        d = src_dict.copy()
        description = d.pop("description", UNSET)

        logs = []
        _logs = d.pop("logs", UNSET)
        for logs_item_data in _logs or []:
            logs_item = LogSpec.from_dict(logs_item_data)

            logs.append(logs_item)

        merged = d.pop("merged", UNSET)

        name = d.pop("name", UNSET)

        summarized = d.pop("summarized", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        _values = d.pop("values", UNSET)
        values: Union[Unset, NewReportValues]
        if isinstance(_values, Unset):
            values = UNSET
        else:
            values = NewReportValues.from_dict(_values)

        new_report = cls(
            description=description,
            logs=logs,
            merged=merged,
            name=name,
            summarized=summarized,
            timestamp=timestamp,
            values=values,
        )

        new_report.additional_properties = d
        return new_report

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
