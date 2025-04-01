from fastapi import FastAPI, HTTPException, APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from datetime import datetime
from typing import Any, Dict, List, Union

from enums import IOCType
from utils import json_serializer
from core import iocs, geo, asn, netflow, client, ipdr
from models import SortOrder
from globals_ import env

http_api = FastAPI(
    docs_url=f"{env.API_PREFIX}/docs", openapi_url=f"{env.API_PREFIX}/openapi.json"
)

router = APIRouter(prefix=env.API_PREFIX)

security = APIKeyHeader(name="X-API-Key")


def api_key_auth():
    if env.DEV:
        return lambda: True

    def check_key(api_key: str = Security(security)):
        if api_key != env.API_KEY:
            raise HTTPException(detail="unauthorized", status_code=400)
        return True

    return check_key


@router.post("/v1/get/iocs", dependencies=[Depends(api_key_auth())], tags=["IOC"])
def _get_iocs(
    page_no: int,
    per_page: int,
    type_: IOCType,
    filters: Dict[str, List] = {},
    sort_by: Union[str, None] = None,
    sort_order: SortOrder = "asc",
    date_from: datetime = None,
    date_to: datetime = None,
):
    return json_serializer(
        iocs.get_iocs(
            page=page_no,
            limit=per_page,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            type_=type_,
            date_from=date_from,
            date_to=date_to,
        )
    )


@router.get("/v1/get/location", dependencies=[Depends(api_key_auth())], tags=["IOC"])
def _get_location(ip: str):
    return json_serializer(geo.get_location(ip))


@router.get("/v1/get/asn", dependencies=[Depends(api_key_auth())], tags=["IOC"])
def _get_asn(ip: str):
    return json_serializer(asn.get_asn_info(ip))


@router.get("/v1/get/entity_info", dependencies=[Depends(api_key_auth())], tags=["IOC"])
def _entity_info(type_: IOCType, val: Any):
    return json_serializer(client.enrich_ioc(type_=type_, ioc=val))


@router.get("/v1/get/ipdr_enrichment", dependencies=[Depends(api_key_auth())], tags=["IOC"])
def _get_viop(ip: str, port: Union[int, None]=None):
    return json_serializer(client.get_ipdr_enrichment(ip=ip, port=port))

@router.post(
    "/v1/get/netflow", dependencies=[Depends(api_key_auth())], tags=["NETFLOW"]
)
def _get_netflow(
    page_no: int,
    per_page: int,
    search_key: Dict[netflow.SearchableFields, str] = {},
    filters: Dict[str, List] = {},
    sort_by: Union[str, None] = None,
    sort_order: SortOrder = "asc",
    date_from: datetime = None,
    date_to: datetime = None,
):
    return json_serializer(
        netflow.get_netflow(
            page=page_no,
            limit=per_page,
            search_key=search_key,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            date_to=date_to,
            date_from=date_from,
        )
    )

@router.get("/v1/get/netflow/countries", dependencies=[Depends(api_key_auth())], tags=["NETFLOW"])
def _get_countries():
    return netflow.get_unique_countries()

http_api.include_router(router)
