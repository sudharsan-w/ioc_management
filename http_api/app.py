from fastapi import FastAPI
from datetime import datetime

from enums import IOCType
from utils import json_serializer
from core import iocs, geo

http_api = FastAPI()


@http_api.get("/v1/get/iocs")
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


@http_api.get("/get/location")
def _get_location(ip: str):
    return json_serializer(geo.get_location(ip))
