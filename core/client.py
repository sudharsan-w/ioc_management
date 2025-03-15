from typing import Any

from enums import IOCType, Lang
from . import iocs, geo, asn


def enrich_ioc(type_: IOCType, ioc: Any):

    meta = {}

    ioc_findings = iocs.get_iocs(type_=type_, skip=0, limit=1, filters={"ioc": [ioc]})
    meta["blacklisted"] = len(ioc_findings) > 0

    if type_ == IOCType.ipv4:
        location = geo.get_location(ip=ioc)
        meta["country"] = location.country.names[Lang.En.value]
        meta["city"] = location.city.names[Lang.En.value]
        meta["region"] = (
            None
            if len(location.subdivisions) == 0
            else location.subdivisions[0].names[Lang.En.value]
        )
        meta["lat"] = location.location.latitude
        meta["long"] = location.location.longitude

        asn_info = asn.get_asn_info(ip=ioc)
        print(asn_info)
        meta = {**meta, **asn_info}

    return {"type_": type_, "entity": ioc, **meta}
