from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TrafficBatchQuery")


@_attrs_define
class TrafficBatchQuery:
    """
    Attributes:
        hids (Union[Unset, List[int]]):
        stats (Union[Unset, List[str]]):
    """

    hids: Union[Unset, List[int]] = UNSET
    stats: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.hids, Unset):
            hids = self.hids

        stats: Union[Unset, List[str]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hids is not UNSET:
            field_dict["hids"] = hids
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hids = cast(List[int], d.pop("hids", UNSET))

        stats = cast(List[str], d.pop("stats", UNSET))

        traffic_batch_query = cls(
            hids=hids,
            stats=stats,
        )

        traffic_batch_query.additional_properties = d
        return traffic_batch_query

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
