from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.new_host_type import NewHostType
from ..types import UNSET, Unset

T = TypeVar("T", bound="NewHost")


@_attrs_define
class NewHost:
    """
    Attributes:
        config_file (Union[Unset, str]):  Example: /home/ericsson/TitanSim.cfg.
        hostname (Union[Unset, str]):  Example: 10.10.10.10.
        install_dir (Union[Unset, str]):  Example: /home/ericsson/TitanSim_R17A01.
        name (Union[Unset, str]):  Example: TS02.
        password (Union[Unset, str]):  Example: klotklot.
        port (Union[Unset, int]):  Example: 8080.
        type (Union[Unset, NewHostType]):  Example: traffic.
        username (Union[Unset, str]):  Example: ericsson.
    """

    config_file: Union[Unset, str] = UNSET
    hostname: Union[Unset, str] = UNSET
    install_dir: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    port: Union[Unset, int] = UNSET
    type: Union[Unset, NewHostType] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config_file = self.config_file

        hostname = self.hostname

        install_dir = self.install_dir

        name = self.name

        password = self.password

        port = self.port

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        username = self.username

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config_file is not UNSET:
            field_dict["config_file"] = config_file
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if install_dir is not UNSET:
            field_dict["install_dir"] = install_dir
        if name is not UNSET:
            field_dict["name"] = name
        if password is not UNSET:
            field_dict["password"] = password
        if port is not UNSET:
            field_dict["port"] = port
        if type is not UNSET:
            field_dict["type"] = type
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        config_file = d.pop("config_file", UNSET)

        hostname = d.pop("hostname", UNSET)

        install_dir = d.pop("install_dir", UNSET)

        name = d.pop("name", UNSET)

        password = d.pop("password", UNSET)

        port = d.pop("port", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, NewHostType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = NewHostType(_type)

        username = d.pop("username", UNSET)

        new_host = cls(
            config_file=config_file,
            hostname=hostname,
            install_dir=install_dir,
            name=name,
            password=password,
            port=port,
            type=type,
            username=username,
        )

        new_host.additional_properties = d
        return new_host

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
