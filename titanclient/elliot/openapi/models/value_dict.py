from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.value import Value


T = TypeVar("T", bound="ValueDict")


@_attrs_define
class ValueDict:
    """
    Attributes:
        config (Union[Unset, List['Value']]):
        gpl (Union[Unset, List['Value']]):
        latency (Union[Unset, List['Value']]):
        status_codes (Union[Unset, List['Value']]):
        traffic (Union[Unset, List['Value']]):
    """

    config: Union[Unset, List["Value"]] = UNSET
    gpl: Union[Unset, List["Value"]] = UNSET
    latency: Union[Unset, List["Value"]] = UNSET
    status_codes: Union[Unset, List["Value"]] = UNSET
    traffic: Union[Unset, List["Value"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.config, Unset):
            config = []
            for componentsschemas_value_list_item_data in self.config:
                componentsschemas_value_list_item = (
                    componentsschemas_value_list_item_data.to_dict()
                )
                config.append(componentsschemas_value_list_item)

        gpl: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.gpl, Unset):
            gpl = []
            for componentsschemas_value_list_item_data in self.gpl:
                componentsschemas_value_list_item = (
                    componentsschemas_value_list_item_data.to_dict()
                )
                gpl.append(componentsschemas_value_list_item)

        latency: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.latency, Unset):
            latency = []
            for componentsschemas_value_list_item_data in self.latency:
                componentsschemas_value_list_item = (
                    componentsschemas_value_list_item_data.to_dict()
                )
                latency.append(componentsschemas_value_list_item)

        status_codes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.status_codes, Unset):
            status_codes = []
            for componentsschemas_value_list_item_data in self.status_codes:
                componentsschemas_value_list_item = (
                    componentsschemas_value_list_item_data.to_dict()
                )
                status_codes.append(componentsschemas_value_list_item)

        traffic: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.traffic, Unset):
            traffic = []
            for componentsschemas_value_list_item_data in self.traffic:
                componentsschemas_value_list_item = (
                    componentsschemas_value_list_item_data.to_dict()
                )
                traffic.append(componentsschemas_value_list_item)

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
        from ..models.value import Value

        d = src_dict.copy()
        config = []
        _config = d.pop("config", UNSET)
        for componentsschemas_value_list_item_data in _config or []:
            componentsschemas_value_list_item = Value.from_dict(
                componentsschemas_value_list_item_data
            )

            config.append(componentsschemas_value_list_item)

        gpl = []
        _gpl = d.pop("gpl", UNSET)
        for componentsschemas_value_list_item_data in _gpl or []:
            componentsschemas_value_list_item = Value.from_dict(
                componentsschemas_value_list_item_data
            )

            gpl.append(componentsschemas_value_list_item)

        latency = []
        _latency = d.pop("latency", UNSET)
        for componentsschemas_value_list_item_data in _latency or []:
            componentsschemas_value_list_item = Value.from_dict(
                componentsschemas_value_list_item_data
            )

            latency.append(componentsschemas_value_list_item)

        status_codes = []
        _status_codes = d.pop("status_codes", UNSET)
        for componentsschemas_value_list_item_data in _status_codes or []:
            componentsschemas_value_list_item = Value.from_dict(
                componentsschemas_value_list_item_data
            )

            status_codes.append(componentsschemas_value_list_item)

        traffic = []
        _traffic = d.pop("traffic", UNSET)
        for componentsschemas_value_list_item_data in _traffic or []:
            componentsschemas_value_list_item = Value.from_dict(
                componentsschemas_value_list_item_data
            )

            traffic.append(componentsschemas_value_list_item)

        value_dict = cls(
            config=config,
            gpl=gpl,
            latency=latency,
            status_codes=status_codes,
            traffic=traffic,
        )

        value_dict.additional_properties = d
        return value_dict

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
