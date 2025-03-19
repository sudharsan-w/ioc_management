from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Union, Mapping, Literal

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


class SourceRef(Model):
    key: str
    type: SourceType


class IOCFinding(Model):
    id: str
    source: str
    source_ref: SourceRef
    ioc_types: List[IOCType]
    keys_: Dict[IOCType, Union[Any, List[Any]]] = Field(..., alias="keys")
    meta: Dict
    source_meta: Dict
    created_at: datetime


class GeoLocation(Model):

    class Cords(Model):
        latitude: float
        longitude: float

    class Country(Model):
        names: Dict[Union[Lang, str], str]

    class Continent(Model):
        names: Dict[Union[Lang, str], str]

    class City(Model):
        names: Dict[Union[Lang, str], str]

    class Subdivision(Model):
        names: Dict[Union[Lang, str], str]

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
