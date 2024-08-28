from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.traffic_stat_defaults import TrafficStatDefaults
    from ..models.traffic_stat_stats import TrafficStatStats


T = TypeVar("T", bound="TrafficStat")


@_attrs_define
class TrafficStat:
    """
    Attributes:
        defaults (Union[Unset, TrafficStatDefaults]):
        hid (Union[Unset, int]):
        hostname (Union[Unset, str]):  Example: TS02.
        scenario (Union[Unset, str]):  Example: 0701PsPs_A.
        stats (Union[Unset, TrafficStatStats]):
    """

    defaults: Union[Unset, "TrafficStatDefaults"] = UNSET
    hid: Union[Unset, int] = UNSET
    hostname: Union[Unset, str] = UNSET
    scenario: Union[Unset, str] = UNSET
    stats: Union[Unset, "TrafficStatStats"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        defaults: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.defaults, Unset):
            defaults = self.defaults.to_dict()

        hid = self.hid

        hostname = self.hostname

        scenario = self.scenario

        stats: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if defaults is not UNSET:
            field_dict["defaults"] = defaults
        if hid is not UNSET:
            field_dict["hid"] = hid
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if scenario is not UNSET:
            field_dict["scenario"] = scenario
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.traffic_stat_defaults import TrafficStatDefaults
        from ..models.traffic_stat_stats import TrafficStatStats

        d = src_dict.copy()
        _defaults = d.pop("defaults", UNSET)
        defaults: Union[Unset, TrafficStatDefaults]
        if isinstance(_defaults, Unset):
            defaults = UNSET
        else:
            defaults = TrafficStatDefaults.from_dict(_defaults)

        hid = d.pop("hid", UNSET)

        hostname = d.pop("hostname", UNSET)

        scenario = d.pop("scenario", UNSET)

        _stats = d.pop("stats", UNSET)
        stats: Union[Unset, TrafficStatStats]
        if isinstance(_stats, Unset):
            stats = UNSET
        else:
            stats = TrafficStatStats.from_dict(_stats)

        traffic_stat = cls(
            defaults=defaults,
            hid=hid,
            hostname=hostname,
            scenario=scenario,
            stats=stats,
        )

        traffic_stat.additional_properties = d
        return traffic_stat

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
