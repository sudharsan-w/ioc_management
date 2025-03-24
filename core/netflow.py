import math
from typing import Dict, Union, List, Literal
from datetime import datetime, timedelta
from sqlalchemy import asc, desc, and_, or_
from sqlalchemy.sql.operators import ilike_op

from globals_ import sql_SessionLocal
from models.sqlalch import NetFlow, IpEnrichment
from models import SortOrder

SearchableFields = Literal["IP", "DOMAIN", "COUNTRY", "ASN"]

def _get_searchable_columns(key: SearchableFields):
    if key == "IP":
        return [NetFlow.ipv4_src_addr ,NetFlow.ipv4_dst_addr]
    if key == "DOMAIN":
        return [NetFlow.src_domain_name, NetFlow.dest_domain_name]
    if key == "COUNTRY":
        return [NetFlow.src_country, NetFlow.dest_country]
    if key == "ASN":
        return [NetFlow.src_asn, NetFlow.dest_asn]
    return []

def get_netflow(
    page: int,
    limit: int,
    search_key: Dict[SearchableFields, str],
    filters: Dict[str, List],
    sort_by: Union[str, None] = None,
    sort_order: SortOrder = "asc",
    date_from: datetime = None,
    date_to: datetime = None,
):
    session = sql_SessionLocal()

    query = session.query(NetFlow)

    ## filters
    if filters:
        for key, vals in filters.items():
            if not hasattr(NetFlow, key):
                e = f"No such field {key} in netflow data"
                raise ValueError(e)
            query = query.filter(getattr(NetFlow, key) in vals)

    ## date filter
    date_to_str = (
        None
        if not date_to
        else (
            (
                date_to.replace(hour=0, minute=0, second=0, microsecond=0)
                + timedelta(days=1)
                - timedelta(seconds=1)
            ).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    date_from_str = (
        None
        if not date_from
        else date_from.replace(hour=0, minute=0, second=0, microsecond=0).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )
    if date_from and date_to:
        query = query.filter(
            and_(NetFlow.flow_start_timestamp) >= date_from_str,
            NetFlow.flow_start_timestamp <= date_to_str,
        )
    elif date_from:
        query = query.filter(NetFlow.flow_start_timestamp >= date_from_str)
    elif date_to:
        query = query.filter(NetFlow.flow_start_timestamp <= date_to_str)

    ## search key
    if search_key: 
        conds = []
        for key, val in search_key.items():
            for column in _get_searchable_columns(key):
                conds.append(ilike_op(column, f"%{val}%"))
        if conds:
            query = query.filter(or_(*conds))

    total_results = query.count()
    if total_results == 0:
        total_pages = 0
        page_no = page
        per_page = 0
        page_no = 0
        has_prev_page = False
        has_next_page = False
        data = []
    else:
        if sort_by:
            query = query.order_by(
                (asc if sort_order == "asc" else desc)(getattr(NetFlow, sort_by))
            )
        query = query.offset((page - 1) * limit).limit(limit)
        data = query.all()
        total_pages = math.ceil(total_results / limit)
        page_no = page
        per_page = min(limit, len(data))
        page_no = page
        has_prev_page = page_no > 1
        has_next_page = page_no < total_pages

    session.close()

    return {
        "data": data,
        "total_results": total_results,
        "total_pages": total_pages,
        "page_no": page_no,
        "per_page": per_page,
        "has_next_page": has_next_page,
        "has_prev_page": has_prev_page,
    }



def get_unique_countries():
    session = sql_SessionLocal()
    query = session.query(NetFlow.src_country).distinct()
    src_countries = [doc[0] for doc in query.all()]
    query = session.query(NetFlow.dest_country).distinct()
    dst_countries = [doc[0] for doc in query.all()]
    session.close()
    return sorted(list(set(dst_countries+src_countries)))

def get_frequency_maps(field: str=None, key: SearchableFields=None):
    session = sql_SessionLocal()
    
    session.close()
    return 

