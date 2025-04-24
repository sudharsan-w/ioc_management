import math
from pytz import UTC
from datetime import datetime, timedelta
from typing import Dict, List, Union, Any

from enums import IOCType
from models import IOCFinding, IOCFindingV2, SortOrder
from database import AppDB
from utils import mongo_serializer


def get_iocs(
    page: int,
    limit: int,
    type_: Union[IOCType, None] = None,
    filters: Dict[str, List] = {},
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
        pipeline.append(
            {"$match": {"created_at": {"$gte": date_from, "$lte": date_to}}}
        )
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


def get_iocs_v2(
    page: int,
    limit: int,
    search_key: Union[str, None] = None,
    filters: Dict[str, List] = {},
    sort_by: Union[str, None] = None,
    sort_order: SortOrder = "asc",
    date_from: datetime = None,
    date_to: datetime = None,
):
    null, true, false = None, True, False
    # return {
    #     "data": [
    #         {
    #             "ioc": "zzzmen99.had.su",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:22:59.013000+00:00",
    #             "last_found_at": "2025-03-05T15:22:59.013000+00:00",
    #             "no_occurrences": 1,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zyxonion.xyz",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:22:57.180000+00:00",
    #             "last_found_at": "2025-03-05T15:22:57.180000+00:00",
    #             "no_occurrences": 1,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zyvcin.xyz",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:22:56.403000+00:00",
    #             "last_found_at": "2025-03-05T15:22:56.403000+00:00",
    #             "no_occurrences": 1,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zxtds.biz",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:23:06.666000+00:00",
    #             "last_found_at": "2025-03-05T15:23:06.666000+00:00",
    #             "no_occurrences": 1,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zxjfcvfvhqfqsrpz.onion",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:23:05.088000+00:00",
    #             "last_found_at": "2025-03-05T15:23:05.096000+00:00",
    #             "no_occurrences": 15,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zwaonoiy.com",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:23:06.963000+00:00",
    #             "last_found_at": "2025-03-05T15:23:06.968000+00:00",
    #             "no_occurrences": 9,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zver.tech",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:22:56.779000+00:00",
    #             "last_found_at": "2025-03-05T15:22:56.779000+00:00",
    #             "no_occurrences": 1,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zunzail.livehost.fr",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:23:02.181000+00:00",
    #             "last_found_at": "2025-03-05T15:23:02.199000+00:00",
    #             "no_occurrences": 2,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zuluworld.ddnsnet.ga",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:23:00.263000+00:00",
    #             "last_found_at": "2025-03-05T15:23:00.263000+00:00",
    #             "no_occurrences": 1,
    #             "no_sources": 1,
    #         },
    #         {
    #             "ioc": "zukkoshop.su",
    #             "type_": "DOMAIN",
    #             "sources_ref": [
    #                 {
    #                     "key": "cybercrime-tracker.net",
    #                     "type": "FEED",
    #                     "attr": {"threat_type": null},
    #                 }
    #             ],
    #             "first_found_at": "2025-03-05T15:23:06.719000+00:00",
    #             "last_found_at": "2025-03-05T15:23:06.719000+00:00",
    #             "no_occurrences": 1,
    #             "no_sources": 1,
    #         },
    #     ],
    #     "total_results": 38695,
    #     "total_pages": 3870,
    #     "page_no": 1,
    #     "per_page": 10,
    #     "has_next_page": true,
    #     "has_prev_page": false,
    # }

    pipeline = [
        {
            "$group": {
                "_id": "$ioc",
                "type_": {"$first": "$type_"},
                "sources_ref": {"$addToSet": "$source_ref"},
                "first_found_at": {"$min": "$created_at"},
                "last_found_at": {"$max": "$created_at"},
                "no_occurrences": {"$sum": 1},
            }
        },
        {"$set": {"no_sources": {"$size": "$sources_ref"}}},
    ]
    # if type_:
    #     pipeline.insert(0, {"$match": {"ioc_types": type_}})
    # pipeline.append({"$unwind": f"$keys.{type_.value}"})
    if search_key:
        pipeline.append({"$match": {"_id": {"$regex": search_key}}})
    if filters:
        for k, v in filters.items():
            if k == "source":
                pipeline.append({"$match": {"sources_ref.key": {"$in": v}}})
            elif k == "threat_type":
                pipeline.append(
                    {"$match": {"sources_ref.attr.threat_type": {"$in": v}}}
                )
            else:
                pipeline.append({"$match": {k: {"$in": v}}})

    date_from = None if not date_from else UTC.localize(date_from)
    date_to = None if not date_to else UTC.localize(date_to)
    if date_from and date_to:
        date_from = date_from + timedelta(days=1)
        date_to = date_to + timedelta(days=2) - timedelta(minutes=1)
        pipeline.append(
            {"$match": {"first_found_at": {"$gte": date_from, "$lte": date_to}}}
        )
    elif date_from:
        date_from = date_from + timedelta(days=1)
        pipeline.append({"$match": {"first_found_at": {"$gte": date_from}}})
    elif date_to:
        date_to = date_to + timedelta(days=2) - timedelta(minutes=1)
        pipeline.append({"$match": {"first_found_at": {"$lte": date_to}}})
    pipeline.append({"$sort": {"_id": -1}})
    # pipeline.append({"$project": {"_id": 0, "source_meta": 0}})
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
    res = AppDB().IOCsV2.aggregate(mongo_serializer(pipeline))
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
    # data = list(map(IOCFindingV2, data))
    data = list(data)
    for d in data:
        d["ioc"] = d["_id"]
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


def ioc_lookup(type_: IOCType, ioc: Any) -> Dict | None:
    pipeline = [
        {"$match": {f"keys.{type_.value}": ioc}},
        {
            "$group": {
                "_id": None,
                "no_occurrences": {"$sum": 1},
                "sources": {"$addToSet": "$source_ref"},
                "meta": {"$addToSet": "$meta.ransomware_group"},
                "first_occurred_at": {"$min": "$meta.date"},
            }
        },
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


def get_type_keys():
    return [v for _, v in IOCType.__members__.items()]
