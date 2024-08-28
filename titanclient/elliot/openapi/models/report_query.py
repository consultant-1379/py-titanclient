from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportQuery")


@_attrs_define
class ReportQuery:
    """
    Attributes:
        filter_ (Union[Unset, str]):  Example: test.
        from_time (Union[Unset, int]):  Example: 1658872799.
        until_time (Union[Unset, int]):  Example: 1958872799.
    """

    filter_: Union[Unset, str] = UNSET
    from_time: Union[Unset, int] = UNSET
    until_time: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        filter_ = self.filter_

        from_time = self.from_time

        until_time = self.until_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filter_ is not UNSET:
            field_dict["filter"] = filter_
        if from_time is not UNSET:
            field_dict["from_time"] = from_time
        if until_time is not UNSET:
            field_dict["until_time"] = until_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        filter_ = d.pop("filter", UNSET)

        from_time = d.pop("from_time", UNSET)

        until_time = d.pop("until_time", UNSET)

        report_query = cls(
            filter_=filter_,
            from_time=from_time,
            until_time=until_time,
        )

        report_query.additional_properties = d
        return report_query

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
