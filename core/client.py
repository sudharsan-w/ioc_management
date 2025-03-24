from typing import Any

from enums import IOCType, Lang
from . import iocs, geo, asn


def enrich_ioc(type_: IOCType, ioc: Any):
    print(ioc)
    meta = {}

    ioc_lookup = iocs.ioc_lookup(type_=type_, ioc=ioc)
    meta["blacklisted"] = False
    meta["blacklisted_sources"] = []
    meta["blacklisted_date"] = None

    if ioc_lookup:
        meta["blacklisted"] = True
        meta["blacklisted_sources"] = ioc_lookup["sources"]
        meta["blacklisted_date"] = ioc["first_occurred_at"]

    if type_ == IOCType.ipv4:
        location = geo.get_location(ip=ioc)
        meta["blacklisted"] = None
        meta["blacklisted_sources"] = None
        meta["country"] = None
        meta["city"] = None
        meta["continent"] = None
        meta["region"] = None
        meta["lat"] = None
        meta["long"] = None
        if location:
            meta["country"] = location.country.names[Lang.En]
            meta["city"] = location.city.names[Lang.En]
            meta["continent"] = location.continent.names[Lang.En]
            meta["region"] = (
                None
                if len(location.subdivisions) == 0
                else location.subdivisions[0].names[Lang.En]
            )
            meta["lat"] = location.location.latitude
            meta["long"] = location.location.longitude
    
        asn_info = asn.get_asn_info(ip=ioc)
        if asn_info:
            meta = {**meta, **asn_info}

    return {"type_": type_, "entity": ioc, **meta}
