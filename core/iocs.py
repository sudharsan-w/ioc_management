from datetime import datetime

from enums import IOCType
from database import AppDB
from utils import mongo_serializer

def get_iocs(
    skip: int,
    limit: int,
    type_: IOCType,
    date_from: datetime = None,
    date_to: datetime = None,
):
    pipeline = []
    pipeline.insert(0, {"$match": {"ioc_types": type_}})
    if date_from and date_to:
        pipeline.append({"$match": {"meta.date": {"$gte": date_from, "$lte": date_to}}})
    elif date_to:
        pipeline.append({"$match": {"meta.date": {"$gte": date_from}}})
    elif date_from:
        pipeline.append({"$match": {"meta.date": {"$lte": date_to}}})
    pipeline.append({"$sort": {"_id": -1}})
    pipeline.extend([{"$skip": skip}, {"$limit": limit}])
    pipeline.append({"$project": {"_id": 0, "source_meta": 0}})
    res = AppDB().IOCs.aggregate(mongo_serializer(pipeline))
    res = list(res)
    return res
    
