import math
from datetime import datetime
from typing import Dict, List, Union, Any

from enums import IOCType
from models import IOCFinding, SortOrder
from database import AppDB
from utils import mongo_serializer


def get_iocs(
    page: int,
    limit: int,
    type_: Union[IOCType, None]=None,
    filters: Dict[str, List]={},
    sort_by: Union[str, None] = None,
    sort_order: SortOrder = "asc",
    date_from: datetime = None,
    date_to: datetime = None,
):
    pipeline = [{"$match": {"source_ref": {"$exists": True}}}]
    if type_:
        pipeline.insert(0, {"$match": {"ioc_types": type_}})
    # pipeline.append({"$unwind": f"$keys.{type_.value}"})
    if filters:
        if "ioc" in filters:
            pipeline.append(
                {"$match": {f"keys.{type_.value}": {"$in": filters["ioc"]}}}
            )
    if date_from and date_to:
        pipeline.append({"$match": {"created_at": {"$gte": date_from, "$lte": date_to}}})
    elif date_to:
        pipeline.append({"$match": {"created_at": {"$gte": date_from}}})
    elif date_from:
        pipeline.append({"$match": {"created_at": {"$lte": date_to}}})
    pipeline.append({"$sort": {"_id": -1}})
    pipeline.append({"$project": {"_id": 0, "source_meta": 0}})
    if sort_by:
        sort = [{"$sort": {sort_by: 1 if sort_order == "asc" else -1}}]
    else:
        sort = []
    pipeline.append(
        {
            "$facet": {
                "agg": [{"$count": "count"}],
                "paginated": [*sort, {"$skip": (page - 1) * limit}, {"$limit": limit}],
            }
        }
    )
    res = AppDB().IOCs.aggregate(mongo_serializer(pipeline))
    res = list(res)
    if len(res) == 0 or len(res[0]["agg"]) == 0:
        total_results = 0
        total_pages = 0
        page_no = 0
        has_prev_page = False
        has_next_page = False
        data = []
    else:
        total_results = res[0]["agg"][0]["count"]
        total_pages = math.ceil(total_results / limit)
        page_no = page
        has_prev_page = page_no > 1
        has_next_page = page_no < total_pages
        data = res[0]["paginated"]
    data = list(map(IOCFinding, data))
    # res = list(map(lambda finding: IOCFinding(**finding), res))
    return {
        "data": data,
        "total_results": total_results,
        "total_pages": total_pages,
        "page_no": page_no,
        "per_page": limit,
        "has_next_page": has_next_page,
        "has_prev_page": has_prev_page,
    }


def ioc_lookup(type_: IOCType, ioc: Any) -> Dict|None:
    pipeline = [
        {"$match": {f"keys.{type_.value}": ioc}},
        {
            "$group": {
                "_id": None,
                "no_occurrences": {"$sum":1},
                "sources": {
                    "$addToSet": "$source_ref"
                },
                "first_occurred_at": {"$min": "$meta.date"}
            }
        }
    ]
    res = AppDB().IOCs.aggregate(pipeline)
    res = list(res)
    if len(res) == 0:
        return None
    res[0]["first_occurred_at"] = res[0].get("first_occurred_at", None)
    if not isinstance(res[0]["first_occurred_at"], datetime):
        res[0]["first_occurred_at"] = None
    if not res[0]["sources"]:
        res[0]["sources"] = []
    return res[0]
