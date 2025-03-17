from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Union

from enums import IOCType, SourceType, Lang


class SourceRef(BaseModel):
    key: str
    type: SourceType


class IOCFinding(BaseModel):
    id: str
    source: str
    source_ref: SourceRef
    ioc_types: List[IOCType]
    keys: Dict[IOCType, Union[Any, List[Any]]]
    meta: Dict
    source_meta: Dict
    created_at: datetime


class GeoLocation(BaseModel):

    class Cords(BaseModel):
        latitude: float
        longitude: float

    class Country(BaseModel):
        names: Dict[Union[Lang, str], str]

    class Continent(BaseModel):
        names: Dict[Union[Lang, str], str]

    class City(BaseModel):
        names: Dict[Union[Lang, str], str]

    class Subdivision(BaseModel):
        names: Dict[Union[Lang, str], str]

    ipv4: str
    location: Cords
    country: Country
    continent: Continent
    city: City
    subdivisions: List[Subdivision] = []
