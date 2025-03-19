from database import AppDB
from models import GeoLocation


def get_location(ip: str):
    octects = ip.split(".")
    octects_copy = [*octects]
    octects_copy[2] = "0"
    octects_copy[3] = "0"
    location = AppDB().GeoLocation.find_one({"ipv4": ".".join(octects_copy)})
    if not location:
        return None
    return GeoLocation(location)
