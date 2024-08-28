from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LogQuery")


@_attrs_define
class LogQuery:
    """
    Attributes:
        from_date (Union[Unset, int]):  Example: 1658786400.
        hids (Union[Unset, List[int]]):
    """

    from_date: Union[Unset, int] = UNSET
    hids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_date = self.from_date

        hids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.hids, Unset):
            hids = self.hids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_date is not UNSET:
            field_dict["from_date"] = from_date
        if hids is not UNSET:
            field_dict["hids"] = hids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_date = d.pop("from_date", UNSET)

        hids = cast(List[int], d.pop("hids", UNSET))

        log_query = cls(
            from_date=from_date,
            hids=hids,
        )

        log_query.additional_properties = d
        return log_query

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
