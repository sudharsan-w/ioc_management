from database import AppDB
from models import ASN

ASN_PROJECTION = lambda: [
    {
        "$project": {
            "_id": 0,
            "asn": "$asn",
            "organization_name": "$name",
            "domain_name": "$domain",
            "entity_type": "$type",
            "tor": {
                "$cond": {
                    "if": {
                        "$and": [
                            {"$ifNull": ["$privacy.tor", False]},
                            {"$ne": ["$privacy.tor", ""]},
                        ]
                    },
                    "then": True,
                    "else": False,
                }
            },
            "proxy": {
                "$cond": {
                    "if": {
                        "$and": [
                            {"$ifNull": ["$privacy.proxy", False]},
                            {"$ne": ["$privacy.tor", ""]},
                        ]
                    },
                    "then": True,
                    "else": False,
                }
            },
            "vpn": {
                "$cond": {
                    "if": {
                        "$and": [
                            {"$ifNull": ["$privacy.vpn", False]},
                            {"$ne": ["$privacy.tor", ""]},
                        ]
                    },
                    "then": True,
                    "else": False,
                }
            },
            "hosting": {
                "$cond": {
                    "if": {
                        "$and": [
                            {"$ifNull": ["$privacy.hosting", False]},
                            {"$ne": ["$privacy.tor", ""]},
                        ]
                    },
                    "then": True,
                    "else": False,
                }
            },
            "relay": {
                "$cond": {
                    "if": {
                        "$and": [
                            {"$ifNull": ["$privacy.relay", False]},
                            {"$ne": ["$privacy.tor", ""]},
                        ]
                    },
                    "then": True,
                    "else": False,
                }
            },
            "service": {
                "$cond": {
                    "if": {
                        "$and": [
                            {"$ifNull": ["$privacy.service", False]},
                            {"$ne": ["$privacy.tor", ""]},
                        ]
                    },
                    "then": True,
                    "else": False,
                }
            },
        }
    }
]


def get_asn_info(ip: str):
    octects = ip.split(".")
    octects_copy = [*octects]
    octects_copy[2] = "0"
    octects_copy[3] = "0"
    pipeline = [{"$match": {"ipv4": ".".join(octects_copy)}}, *ASN_PROJECTION()]
    res = AppDB().ASNRecords.aggregate(pipeline)
    res = list(map(ASN, res))
    return None if len(res) == 0 else res[0]
