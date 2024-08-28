from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cache_status import CacheStatus


T = TypeVar("T", bound="LogStatus")


@_attrs_define
class LogStatus:
    """
    Attributes:
        config (Union[Unset, CacheStatus]):
        gpl (Union[Unset, CacheStatus]):
        latency (Union[Unset, CacheStatus]):
        status_codes (Union[Unset, CacheStatus]):
    """

    config: Union[Unset, "CacheStatus"] = UNSET
    gpl: Union[Unset, "CacheStatus"] = UNSET
    latency: Union[Unset, "CacheStatus"] = UNSET
    status_codes: Union[Unset, "CacheStatus"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        gpl: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.gpl, Unset):
            gpl = self.gpl.to_dict()

        latency: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.latency, Unset):
            latency = self.latency.to_dict()

        status_codes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.status_codes, Unset):
            status_codes = self.status_codes.to_dict()

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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.cache_status import CacheStatus

        d = src_dict.copy()
        _config = d.pop("config", UNSET)
        config: Union[Unset, CacheStatus]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = CacheStatus.from_dict(_config)

        _gpl = d.pop("gpl", UNSET)
        gpl: Union[Unset, CacheStatus]
        if isinstance(_gpl, Unset):
            gpl = UNSET
        else:
            gpl = CacheStatus.from_dict(_gpl)

        _latency = d.pop("latency", UNSET)
        latency: Union[Unset, CacheStatus]
        if isinstance(_latency, Unset):
            latency = UNSET
        else:
            latency = CacheStatus.from_dict(_latency)

        _status_codes = d.pop("status_codes", UNSET)
        status_codes: Union[Unset, CacheStatus]
        if isinstance(_status_codes, Unset):
            status_codes = UNSET
        else:
            status_codes = CacheStatus.from_dict(_status_codes)

        log_status = cls(
            config=config,
            gpl=gpl,
            latency=latency,
            status_codes=status_codes,
        )

        log_status.additional_properties = d
        return log_status

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
