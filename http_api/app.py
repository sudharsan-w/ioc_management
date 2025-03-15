from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from datetime import datetime
from typing import Any

from enums import IOCType
from utils import json_serializer
from core import iocs, geo, client
from globals_ import env

http_api = FastAPI()

security = APIKeyHeader(name="X-API-Key")


def api_key_auth():
    if env.DEV:
        return lambda *_: True

    def check_key(api_key: str = Security(security)):
        if api_key != env.API_KEY:
            raise HTTPException(detail="unauthorized", status_code=400)
        return True

    return check_key


@http_api.get("/v1/get/iocs", dependencies=[Depends(api_key_auth())])
def _get_iocs(
    page_no: int,
    per_page: int,
    type_: IOCType,
    date_from: datetime = None,
    date_to: datetime = None,
):
    return json_serializer(
        iocs.get_iocs(
            skip=(page_no * per_page),
            limit=per_page,
            type_=type_,
            date_from=date_from,
            date_to=date_to,
        )
    )


@http_api.get("/v1/get/location", dependencies=[Depends(api_key_auth())])
def _get_location(ip: str):
    return json_serializer(geo.get_location(ip))


@http_api.get("/v1/get/entity_info", dependencies=[Depends(api_key_auth())])
def _entity_info(type_: IOCType, val: Any):
    return json_serializer(client.enrich_ioc(type_=type_, ioc=val))
