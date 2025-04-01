from typing import Any

from enums import IOCType, Lang
from . import iocs, geo, asn, sources, ipdr


def enrich_ioc(type_: IOCType, ioc: Any):

    meta = {}

    ioc_lookup = iocs.ioc_lookup(type_=type_, ioc=ioc)
    meta["blacklisted"] = False
    meta["blacklisted_sources"] = []
    meta["blacklisted_date"] = None
    meta["threat_types"] = []

    if ioc_lookup:
        meta["blacklisted"] = True
        meta["blacklisted_sources"] = [s["key"] for s in ioc_lookup["sources"]]
        meta["blacklisted_date"] = ioc_lookup["first_occurred_at"]

    sources_ = sources.get_ioc_sources(type_=type_, ioc=ioc)
    if sources_:
        for source in sources_:
            if threat_type := source.attribution.get("threat_type"):
                meta["threat_types"].append(threat_type)
            if source.key not in meta["blacklisted_sources"]:
                meta["blacklisted_sources"].append(source.key)

    if type_ == IOCType.ipv4:
        if ":" in ioc:
            ip, port = ioc.split(":")
            port = int(port)
        else:
            ip, port = ioc, None
        location = geo.get_location(ip=ip)
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

        asn_info = asn.get_asn_info(ip=ip)
        meta["asn"] = None
        meta["organization_name"] = None
        meta["domain_name"] = None
        meta["entity_type"] = None
        meta["tor"] = None
        meta["proxy"] = None
        meta["vpn"] = None
        meta["hosting"] = None
        meta["relay"] = None
        meta["service"] = None
        if asn_info:
            meta = {**meta, **asn_info}

        
        org = None if not port else ipdr.get_voip_application(ip=ip, port=port)
        meta["is_voip"] = False
        meta["voip_app"] = None
        if org:
            meta["is_voip"] = True
            meta["voip_app"] = org.name

    return {"type_": type_, "entity": ioc, **meta}


def get_ipdr_enrichment(ip: str, port: int = None):
    networks = ipdr.get_networks(ip)
    orgs = ipdr.get_organizations(ip)
    voip_app = None
    if port:
        voip_app = ipdr.get_voip_application(ip, port)
    
    return {
        "networks": [{"host_addr": network.host_addr, "network_addr": network.network_addr} for network in networks],
        "organization": [{"name": org.name} for org in orgs],
        "voip_app": None if not voip_app else voip_app.name
    }