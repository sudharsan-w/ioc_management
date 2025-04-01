from pydantic import BaseModel, Field
from pydantic_core import core_schema
from datetime import datetime
from typing import List, Dict, Any, Union, Mapping, Literal, Annotated
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

from enums import IOCType, SourceType, Lang

SortOrder = Literal["asc", "desc"]


class Model(BaseModel):

    def __init__(self, data=None, **kwargs):
        if isinstance(data, Mapping):
            kwargs = {**data, **kwargs}
        super().__init__(**kwargs)

    def keys(self):
        return list(self)

    def __getitem__(self, key):
        if key not in self.model_fields:
            e = f"{key} not found"
            raise KeyError(e)
        return getattr(self, key)

    def __iter__(self):
        return iter(self.model_fields)

    def __len__(self):
        return len(self.model_fields)

    def __repr__(self):
        return f"{self.__class__.__name__}({self})"

    model_config = {"populate_by_name": True}


class Source(Model):
    id: str
    type: SourceType
    key: str
    # url: str
    created_at: datetime
    attribution: Dict = {}


class StorageBucketSource(Source):
    type: SourceType = SourceType.storage_bucket
    bucketname: Union[str, None] = None
    username_space: Union[str, None] = None


class MISPSource(Source):
    type: SourceType = SourceType.misp


class FeedSource(Source):
    type: SourceType = SourceType.feed


class SourceRef(Model):
    key: str
    type: SourceType


class IOCFinding(Model):
    id: str
    source: str
    source_ref: Union[SourceRef, None] = None
    ioc_types: List[IOCType]
    keys: Dict[IOCType, Union[Any, List[Any]]] = Field(..., alias="keys")
    meta: Dict = {}
    source_meta: Dict = {}
    created_at: datetime


class Names(Dict[Lang, str]):

    @classmethod
    def validate(cls, val):
        if not isinstance(val, Mapping):
            e = f"{cls.__name__} expects a dictionary, but received a {type(val).__name__}"
            raise TypeError(e)
        return {
            Lang._value2member_map_[k]: v
            for k, v in val.items()
            if k in Lang._value2member_map_
        }

    @classmethod
    def __get_pydantic_core_schema__(cls, _, __):
        return core_schema.chain_schema(
            [
                core_schema.dict_schema(),
                core_schema.no_info_plain_validator_function(lambda v: cls.validate(v)),
            ]
        )


class GeoLocation(Model):

    class Cords(Model):
        latitude: float
        longitude: float

    class Country(Model):
        names: Names

    class Continent(Model):
        names: Names

    class City(Model):
        names: Names

    class Subdivision(Model):
        names: Names

    ipv4: str
    location: Cords
    country: Country
    continent: Continent
    city: City
    subdivisions: List[Subdivision] = []


class ASN(Model):
    asn: str
    organization_name: str
    domain_name: str
    entity_type: str
    tor: bool
    proxy: bool
    vpn: bool
    hosting: bool
    relay: bool
    service: bool


SourceTypeVar = Annotated[
    Union[MISPSource, FeedSource, StorageBucketSource], Field(discriminator="type")
]


def create_source(*args, **kwargs):
    if len(args) > 0:
        source_type = args[0].get("type")
    if "type" in kwargs:
        source_type = kwargs["type"]
    source_type = SourceType(source_type)

    if source_type == SourceType.misp:
        return MISPSource(*args, **kwargs)
    if source_type == SourceType.feed:
        return FeedSource(*args, **kwargs)
    if source_type == SourceType.storage_bucket:
        return StorageBucketSource(*args, **kwargs)


class Network(Model):
    class OrgRef(Model):
        name: str
        id: str
    id: str
    host_addr: Union[IPv4Network, IPv6Network]
    broadcast_addr: Union[IPv4Address, IPv6Address]
    network_addr: Union[IPv4Address, IPv6Address]
    netmask: Union[IPv4Address, IPv6Address]
    host_mask: Union[IPv4Address, IPv6Address]
    # hosts: List[str]
    network_st: str
    network_en: str
    belongs_to: Union[OrgRef, None] = None


class Organization(Model):
    id: str
    name: str
    voip_ports: list[int]
