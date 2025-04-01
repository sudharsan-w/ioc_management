import ipaddress
from typing import List

from database import AppDB
from models import Network, Organization
from utils import mongo_serializer, ID



def _get_network_range(ip: str):
    network = ipaddress.ip_network(ip)
    return int(network.network_address), int(network.broadcast_address)


def _ip_ord(ip: str):
    return int(ipaddress.ip_address(ip))


def get_networks(ip: str) -> List[Network]:
    ip_val = str(_ip_ord(ip))
    networks = AppDB().Networks.find(
        {
            "$expr": {
                "$and": [
                    {"$lte": ["$network_st", ip_val]},
                    {"$gte": ["$network_en", ip_val]},
                ]
            }
        }
    )
    networks = list(map(Network, networks))
    return networks

def get_organizations(ip: str) -> List[Organization]:
    networks = get_networks(ip)
    org_ids = [network.belongs_to.id for network in networks if network.belongs_to]
    orgs = AppDB().Organizations.find({"id": {"$in": org_ids}}).sort("name", 1)
    orgs = list(map(Organization, orgs))
    return orgs

def get_voip_application(ip: str, port: int) -> Organization|None:
    port = int(port)
    orgs = get_organizations(ip)
    for org in orgs:
        if port in org.voip_ports:
            return org
    return None
    

def _network(ip: str, belongs_to_id: str, belongs_to_name: str):
    network_ = ipaddress.ip_network(ip)
    network_st, network_en = _get_network_range(ip)
    network = Network(
        id=ID(),
        host_addr=network_,
        broadcast_addr=network_.broadcast_address,
        network_addr=network_.network_address,
        host_mask=network_.hostmask,
        netmask=network_.netmask,
        # hosts=network_.hosts(),
        network_en=str(network_en),
        network_st=str(network_st),
        belongs_to=Network.OrgRef(id=belongs_to_id, name=belongs_to_name)
    )
    AppDB().Networks.insert_one(mongo_serializer(network))
    

