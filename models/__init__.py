from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Union

from enums import IOCType, SourceType


class SourceRef(BaseModel):
    key: str
    type: SourceType


class IOCFinding(BaseModel):
    id: str
    source: str
    source_ref: SourceRef
    ioc_types: List[IOCType]
    keys: Dict[IOCType, Union[Any, List[Any]]]
    meta: Dict
    source_meta: Dict
    created_at: datetime
