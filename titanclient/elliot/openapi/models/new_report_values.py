from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NewReportValues")


@_attrs_define
class NewReportValues:
    """
    Attributes:
        config (Union[Unset, List[str]]):
        gpl (Union[Unset, List[str]]):
        latency (Union[Unset, List[str]]):
        status_codes (Union[Unset, List[str]]):
        traffic (Union[Unset, List[str]]):
    """

    config: Union[Unset, List[str]] = UNSET
    gpl: Union[Unset, List[str]] = UNSET
    latency: Union[Unset, List[str]] = UNSET
    status_codes: Union[Unset, List[str]] = UNSET
    traffic: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config: Union[Unset, List[str]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config

        gpl: Union[Unset, List[str]] = UNSET
        if not isinstance(self.gpl, Unset):
            gpl = self.gpl

        latency: Union[Unset, List[str]] = UNSET
        if not isinstance(self.latency, Unset):
            latency = self.latency

        status_codes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.status_codes, Unset):
            status_codes = self.status_codes

        traffic: Union[Unset, List[str]] = UNSET
        if not isinstance(self.traffic, Unset):
            traffic = self.traffic

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config is not UNSET:
            field_dict["config"] = config
        if gpl is not UNSET:
            field_dict["gpl"] = gpl
        if latency is not UNSET:
            field_dict["latency"] = latency
        if status_codes is not UNSET:
            field_dict["status_codes"] = status_codes
        if traffic is not UNSET:
            field_dict["traffic"] = traffic

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        config = cast(List[str], d.pop("config", UNSET))

        gpl = cast(List[str], d.pop("gpl", UNSET))

        latency = cast(List[str], d.pop("latency", UNSET))

        status_codes = cast(List[str], d.pop("status_codes", UNSET))

        traffic = cast(List[str], d.pop("traffic", UNSET))

        new_report_values = cls(
            config=config,
            gpl=gpl,
            latency=latency,
            status_codes=status_codes,
            traffic=traffic,
        )

        new_report_values.additional_properties = d
        return new_report_values

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
