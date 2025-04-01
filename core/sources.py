from uuid import uuid4
from datetime import datetime
from urllib.parse import urlparse

from database import AppDB
from typing import Any
from enums import IOCType, SourceType
from models import IOCFinding, SourceRef, SourceTypeVar, create_source
from utils import mongo_serializer, curr_time


def get_git_user_repo(url: str):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")

    if "githubusercontent.com" in parsed_url.netloc:
        if len(path_parts) >= 2:
            return path_parts[0], path_parts[1]

    elif "gitlab.io" in parsed_url.netloc:
        subdomain = parsed_url.netloc.split(".")[0]
        repo_name = path_parts[0] if path_parts else None
        return subdomain, repo_name
    return None, None


def get_git_repo_url(url: str):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")

    if "githubusercontent.com" in parsed_url.netloc:
        if len(path_parts) >= 2:
            user, repo = path_parts[0], path_parts[1]
            return f"https://github.com/{user}/{repo}"

    elif "gitlab.io" in parsed_url.netloc:
        subdomain = parsed_url.netloc.split(".")[0]
        repo_name = path_parts[0] if path_parts else None
        if repo_name:
            return f"https://gitlab.com/{subdomain}/{repo_name}"
        else:
            return f"https://gitlab.com/{subdomain}"

    return None


def extract_domain(s):
    s = s.replace("https://", "")
    s = s.replace("http://", "")
    s = s.replace("www.", "")
    s = s.split("/")[0]
    return s


def _normalized_source(doc) -> SourceTypeVar:
    if str(doc.get("source_meta", {}).get("type")).lower() == "misp":
        source = {
            "id": str(uuid4()),
            "type": SourceType.misp.value,
            "key": extract_domain(doc["source"].replace(doc["source"].split("/")[-1], "")),
            "url": doc["source"].replace(doc["source"].split("/")[-1], ""),
            "created_at": datetime.now(),
        }
    elif "github" in doc["source"]:
        source = {
            "id": str(uuid4()),
            "type": SourceType.storage_bucket.value,
            "key": f"github.com/{get_git_user_repo(doc['source'])[0]}/{get_git_user_repo(doc['source'])[1]}",
            "username_space": get_git_user_repo(doc["source"])[0],
            "bucketname": get_git_user_repo(doc["source"])[1],
            "url": get_git_repo_url(doc["source"]),
            "created_at": datetime.now(),
        }

    elif "gitlab" in doc["source"]:
        source = {
            "id": str(uuid4()),
            "type": SourceType.storage_bucket.value,
            "key": f"gitlab.com/{get_git_user_repo(doc['source'])[0]}/{get_git_user_repo(doc['source'])[1]}",
            "username_space": get_git_user_repo(doc["source"])[0],
            "bucketname": get_git_user_repo(doc["source"])[1],
            "url": get_git_repo_url(doc["source"]),
            "created_at": datetime.now(),
        }
    else:
        source = {
            "id": str(uuid4()),
            "type": SourceType.feed.value,
            "key": extract_domain(doc["source"]),
            "created_at": datetime.now(),
        }
    return create_source(source)


def get_source(type_: SourceType, key: str) -> SourceTypeVar|None:
    source = AppDB().IOCSources.find_one(mongo_serializer({"type": type_, "key": key}))
    print(source, mongo_serializer({"type": type_, "key": key}))
    source = None if not source else create_source(source)
    return source

def add_source(source: SourceTypeVar):
    if ex:=get_source(source.type, source.key):
        return ex
    source.created_at = curr_time()
    AppDB().IOCSources.insert_one(mongo_serializer(source))
    return source

def normalize_source(ioc_finding: IOCFinding):
    source = _normalized_source(ioc_finding.model_dump(by_alias=True))
    source = add_source(source)
    return source

def get_ioc_sources(type_: IOCType, ioc: Any):

    sources_refs = AppDB().IOCs.aggregate([
        {
            "$match": {f"keys.{type_.value}": ioc}
        },
        {
            "$group": {
                "_id": None,
                "source_refs": {
                    "$addToSet": "$source_ref"
                }
            }
        }
    ])
    sources_refs = list(sources_refs)
    sources_refs = [] if len(sources_refs)==0 else sources_refs[0].get("source_refs", [])
    sources_refs = list(map(SourceRef, sources_refs))
    
    return list(map(lambda s: get_source(s.type, s.key), sources_refs))
    # if ioc_finding.source_ref:
    #     return get_source(ioc_finding.source_ref.type, ioc_finding.source_ref.key)
    
    # return normalize_source(ioc_finding)
    
