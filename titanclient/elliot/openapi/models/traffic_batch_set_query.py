from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.traffic_batch_set_query_values import TrafficBatchSetQueryValues


T = TypeVar("T", bound="TrafficBatchSetQuery")


@_attrs_define
class TrafficBatchSetQuery:
    """
    Attributes:
        hids (Union[Unset, List[int]]):
        stats (Union[Unset, List[str]]):
        values (Union[Unset, TrafficBatchSetQueryValues]):
    """

    hids: Union[Unset, List[int]] = UNSET
    stats: Union[Unset, List[str]] = UNSET
    values: Union[Unset, "TrafficBatchSetQueryValues"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.hids, Unset):
            hids = self.hids

        stats: Union[Unset, List[str]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats

        values: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.values, Unset):
            values = self.values.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hids is not UNSET:
            field_dict["hids"] = hids
        if stats is not UNSET:
            field_dict["stats"] = stats
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.traffic_batch_set_query_values import TrafficBatchSetQueryValues

        d = src_dict.copy()
        hids = cast(List[int], d.pop("hids", UNSET))

        stats = cast(List[str], d.pop("stats", UNSET))

        _values = d.pop("values", UNSET)
        values: Union[Unset, TrafficBatchSetQueryValues]
        if isinstance(_values, Unset):
            values = UNSET
        else:
            values = TrafficBatchSetQueryValues.from_dict(_values)

        traffic_batch_set_query = cls(
            hids=hids,
            stats=stats,
            values=values,
        )

        traffic_batch_set_query.additional_properties = d
        return traffic_batch_set_query

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
