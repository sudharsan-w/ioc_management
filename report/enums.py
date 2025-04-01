from enum import Enum

from . import client
from .base import DataModel, DataSlice

_report_data_model_names = {}
_report_data_models = {}
_report_data_slice_names = {}
_report_data_slices = {}

for member_name in client.__dir__():
    member = getattr(client, member_name)
    if isinstance(member, type):
        if member.__name__ == DataModel.__name__:
            pass
        elif issubclass(member, DataModel):
            _report_data_models[member.__name__] = member
            _report_data_model_names[member.__name__] = member.__name__

        if member.__name__ == DataSlice.__name__:
            pass
        elif issubclass(member, DataSlice):
            _report_data_slices[member.__name__] = member
            _report_data_slice_names[member.__name__] = member.__name__

ReportDataModel = Enum("ReportDataModel", _report_data_model_names)
ReportDataSlice = Enum("ReportDataSlice", _report_data_slice_names)


def get_model(key: ReportDataModel) -> DataModel:
    return _report_data_models.get(key.value, None)


def get_slice(key: ReportDataSlice) -> DataSlice:
    return _report_data_slices.get(key.value, None)



class FileType(Enum):
    CSV = "csv"
    JSON = "json"


class DataRange(Enum):
    ALL = "all"
    PREV_DAY = "prev_day"


class ItemType(Enum):
    FILE = "file"
    CUSTOM = "custom"


class FileType(Enum):
    CSV = "csv"
    ZIP = "zip"
    JSON = "json"
    SPREAD_SHEET = "spread_sheet"


class SpreadSheetContentType(Enum):
    DATA_FRAME = "data_frame"
    SCALAR = "scalar"
    GRAPH = "graph"


class ChartType(Enum):
    PIE = "pie"
    BAR = "bar"
    LINE = "line"


class GoogleAccessLevel(Enum):
    READ = "read"
    WRITE = "write"


class DriveService(Enum):
    GOOGLE = "google"
    ONEDRIVE = "one_drive"
