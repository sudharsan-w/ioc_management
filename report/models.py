from pydantic import BaseModel, field_validator
from typing import Union

from .enums import (
    DriveService,
    DataRange,
    FileType,
    ItemType,
    ChartType,
    SpreadSheetContentType,
)
from .enums import ReportDataModel, ReportDataSlice
from .misc.google import Role as GoogleRole
from utils import curr_time, ID


class DateFormat(BaseModel):
    datefmt: str

    @field_validator("datefmt")
    def _datefmt(val: str):
        try:
            curr_time().strftime(val)
        except:
            raise ValueError("not a valid date format")
        return val


class Content(BaseModel):
    slice_name: str
    data: str = "all"


TemplateString = Union[str, list[Union[str, DateFormat]]]
DataCount = Union[int, DataRange]


class SpreadSheetContent(Content):
    content_type: SpreadSheetContentType


class SpreadSheetGraph(SpreadSheetContent):
    content_type: SpreadSheetContentType = SpreadSheetContentType.GRAPH
    title: TemplateString
    chart_type: ChartType
    category_field: str
    data_field: str


class SpreadSheetScalarContent(SpreadSheetContent):
    content_type: SpreadSheetContentType = SpreadSheetContentType.SCALAR
    title: TemplateString


class SpreadSheetDataFrame(SpreadSheetContent):
    content_type: SpreadSheetContentType = SpreadSheetContentType.DATA_FRAME
    projection: Union[list[str], None] = None


SpreadSheetContentTypeVar = Union[
    SpreadSheetContent,
    SpreadSheetScalarContent,
    SpreadSheetDataFrame,
    SpreadSheetGraph,
]


class Sheet(BaseModel):
    title: TemplateString
    content: list[SpreadSheetContentTypeVar]


class Item(BaseModel):
    type: ItemType


class CustomItem(Item):
    pass


class File(Item):
    type: ItemType = ItemType.FILE
    file_type: FileType
    path: TemplateString


class SpreadSheet(File):
    # title: TemplateString
    file_type: FileType = FileType.SPREAD_SHEET
    sheets: list[Sheet]


class Zip(File):
    file_type: FileType = FileType.ZIP


class DataSliceConfig(BaseModel):
    name: str
    model: ReportDataModel
    slice_engine: ReportDataSlice
    count: DataCount


class GoogleAccess(BaseModel):
    access_to: str
    access_level: GoogleRole


class DriveConfig(BaseModel):
    service: DriveService


class OneDriveConfig(DriveConfig):
    service: DriveService = DriveService.ONEDRIVE
    email: str


class GoogleDriveConfig(DriveConfig):
    service: DriveService = DriveService.GOOGLE
    share_with: list[GoogleAccess]


DriveConfigTypeVar = Union[DriveConfig, GoogleDriveConfig, OneDriveConfig]

ItemTypeVar = Union[Item, File, Zip, SpreadSheet, CustomItem]


class ReportAPI(BaseModel):
    name: str
    data_slices: list[DataSliceConfig]
    items: list[ItemTypeVar]
    share: Union[DriveConfigTypeVar]
    schedule: str


class Report(ReportAPI):
    id: str
