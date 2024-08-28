from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.log_spec import LogSpec


T = TypeVar("T", bound="LogStatQuery")


@_attrs_define
class LogStatQuery:
    """
    Attributes:
        logs (Union[Unset, List['LogSpec']]):
        stats (Union[Unset, List[str]]):
    """

    logs: Union[Unset, List["LogSpec"]] = UNSET
    stats: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        logs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.logs, Unset):
            logs = []
            for logs_item_data in self.logs:
                logs_item = logs_item_data.to_dict()
                logs.append(logs_item)

        stats: Union[Unset, List[str]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if logs is not UNSET:
            field_dict["logs"] = logs
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.log_spec import LogSpec

        d = src_dict.copy()
        logs = []
        _logs = d.pop("logs", UNSET)
        for logs_item_data in _logs or []:
            logs_item = LogSpec.from_dict(logs_item_data)

            logs.append(logs_item)

        stats = cast(List[str], d.pop("stats", UNSET))

        log_stat_query = cls(
            logs=logs,
            stats=stats,
        )

        log_stat_query.additional_properties = d
        return log_stat_query

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
