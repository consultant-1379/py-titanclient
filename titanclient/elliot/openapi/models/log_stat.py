from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.log_stat_stats import LogStatStats


T = TypeVar("T", bound="LogStat")


@_attrs_define
class LogStat:
    """
    Attributes:
        hid (Union[Unset, int]):
        hostname (Union[Unset, str]):  Example: TS02.
        lid (Union[Unset, str]):
        scenario (Union[Unset, str]):  Example: 0701PsPs_A.
        stats (Union[Unset, LogStatStats]):
    """

    hid: Union[Unset, int] = UNSET
    hostname: Union[Unset, str] = UNSET
    lid: Union[Unset, str] = UNSET
    scenario: Union[Unset, str] = UNSET
    stats: Union[Unset, "LogStatStats"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hid = self.hid

        hostname = self.hostname

        lid = self.lid

        scenario = self.scenario

        stats: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hid is not UNSET:
            field_dict["hid"] = hid
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if lid is not UNSET:
            field_dict["lid"] = lid
        if scenario is not UNSET:
            field_dict["scenario"] = scenario
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.log_stat_stats import LogStatStats

        d = src_dict.copy()
        hid = d.pop("hid", UNSET)

        hostname = d.pop("hostname", UNSET)

        lid = d.pop("lid", UNSET)

        scenario = d.pop("scenario", UNSET)

        _stats = d.pop("stats", UNSET)
        stats: Union[Unset, LogStatStats]
        if isinstance(_stats, Unset):
            stats = UNSET
        else:
            stats = LogStatStats.from_dict(_stats)

        log_stat = cls(
            hid=hid,
            hostname=hostname,
            lid=lid,
            scenario=scenario,
            stats=stats,
        )

        log_stat.additional_properties = d
        return log_stat

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
