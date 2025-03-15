import re
import uuid
from bson import ObjectId
from datetime import datetime
from enum import Enum
from pytz import timezone
from pydantic import BaseModel

from globals_ import env

ID = lambda: str(uuid.uuid4())


def to_utc(dt_obj: datetime, tz=env.DEFAULT_TIME_ZONE):
    if dt_obj.tzinfo == None:
        dt_obj = tz.localize(dt=dt_obj)
    return dt_obj.astimezone(timezone("UTC"))


def to_tz(dt_obj: datetime, to_tz, curr_tz=env.DEFAULT_TIME_ZONE):
    if dt_obj.tzinfo == None:
        dt_obj = curr_tz.localize(dt=dt_obj)
    return dt_obj.astimezone(to_tz)


def curr_time():
    return to_utc(datetime.now().astimezone())


def extract_url_domain(s):
    s = s.replace("http://", "")
    s = s.replace("https://", "")
    s = s if not s.startswith("www.") else s[4:]
    s = s if not "/" in s else s[: s.index("/")]
    s = s if not "?" in s else s[: s.index("?")]
    s = s.replace('"', "")
    return s


def mongo_serializer(obj):
    func_ = mongo_serializer
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return to_utc(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, BaseModel):
        return func_(vars(obj))
    if isinstance(obj, list):
        return [func_(e) for e in obj]
    if isinstance(obj, dict):
        return {func_(k): func_(v) for k, v in obj.items()}
    return obj


def json_serializer(obj):
    func_ = json_serializer
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, BaseModel):
        return func_(vars(obj))
    if isinstance(obj, list):
        return [func_(e) for e in obj]
    if isinstance(obj, dict):
        return {func_(k): func_(v) for k, v in obj.items()}
    return obj


def timezone_updater(obj, tz):
    func_ = timezone_updater
    if isinstance(obj, datetime):
        return to_tz(obj, tz)
    elif isinstance(obj, list):
        return [func_(e, tz) for e in obj]
    elif isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = func_(v, tz)
    elif isinstance(obj, BaseModel):
        for k, v in obj.dict().items():
            obj.__setattr__(k, func_(v, tz))
    return obj


def is_valid_vpa(txt):
    pattern = r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$"
    matched = re.match(pattern, txt)
    return matched


def if_null(*args):
    for arg in args:
        if not args:
            return arg
