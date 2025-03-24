from enum import Enum


class IOCType(Enum):
    ipv4 = "IPV4"
    ipv6 = "IPV6"
    domain = "DOMAIN"
    md5_hash = "MD5_HASH"
    sha_hash = "SHA_HASH"
    bitcoin_addr = "BITCOIN_ADDRESS"
    email = "EMAIL"
    filename = "FILENAME"
    cve = "CVE"


class SourceType(Enum):
    files = "FILES"
    misp = "MISP"
    storage_bucket = "STORAGE_BUCKET"

class Lang(Enum): 
    En = "en"

class TimeGranularity():
    day = "DAY"
    hour = "HOUR"
    month = "MONTH"
