from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from datetime import datetime
from typing import Any, Dict, List

from enums import IOCType
from utils import json_serializer
from core import iocs, geo, asn, client
from globals_ import env

http_api = FastAPI()

security = APIKeyHeader(name="X-API-Key")


def api_key_auth():
    if env.DEV:
        return lambda: True

    def check_key(api_key: str = Security(security)):
        if api_key != env.API_KEY:
            raise HTTPException(detail="unauthorized", status_code=400)
        return True

    return check_key


@http_api.post("/v1/get/iocs", dependencies=[Depends(api_key_auth())])
def _get_iocs(
    page_no: int,
    per_page: int,
    type_: IOCType,
    filters: Dict[str, List] = {},
    date_from: datetime = None,
    date_to: datetime = None,
):
    return json_serializer(
        iocs.get_iocs(
            skip=(page_no * per_page),
            limit=per_page,
            filters=filters,
            type_=type_,
            date_from=date_from,
            date_to=date_to,
        )
    )


@http_api.get("/v1/get/location", dependencies=[Depends(api_key_auth())])
def _get_location(ip: str):
    return json_serializer(geo.get_location(ip))

@http_api.get("/v1/get/asn", dependencies=[Depends(api_key_auth())])
def _get_asn(ip: str):
    return json_serializer(asn.get_asn_info(ip))


@http_api.get("/v1/get/entity_info", dependencies=[Depends(api_key_auth())])
def _entity_info(type_: IOCType, val: Any):
    return json_serializer(client.enrich_ioc(type_=type_, ioc=val))
