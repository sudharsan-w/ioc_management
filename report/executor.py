import os
import shutil
from typing import Iterable
from datetime import timedelta

from .models import (
    Report,
    ReportAPI,
    Item,
    File,
    Sheet,
    Content,
    CustomItem,
    SpreadSheet,
    DataSliceConfig,
    SpreadSheetContent,
    SpreadSheetDataFrame,
    SpreadSheetGraph,
    DateFormat,
    DataRange,
    DriveConfig,
    GoogleDriveConfig,
    TemplateString,
)
from .enums import ReportDataSlice
from .enums import FileType, SpreadSheetContentType
from .base import ScalarType, DataModel, DataSlice
from .misc.spread_sheet import SpreadsheetManager
from .misc.google import GoogleDrive, LocalFile
from .enums import get_model, get_slice
from utils import json_serializer, csv_serializer, mongo_serializer, curr_time, date_from_datetime, ID

from globals_ import env, default_google_conn
from core.iocs import get_iocs
from enums import IOCType

def evaluate_template_string(
    value: TemplateString, date_=curr_time() + timedelta(days=1)
) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, DateFormat):
        return date_.strftime(value.datefmt)
    if isinstance(value, Iterable):
        eval_ = ""
        for item in value:
            eval_ += evaluate_template_string(item)
        return eval_



class ReportCheker:

    def __init__(self, report: Report):
        self._report = report

    def _get_slice_names(self):
        if "_slice_names" in self.__dir__():
            return self._slice_names
        self._slice_names = [ds.name for ds in self._report.data_slices]
        return self._slice_names

    def _get_slice(self, name):
        for ds in self._report.data_slices:
            if ds.name == name:
                return ds
        return None

    def _check_data_slice_config(self, configs: list[DataSliceConfig]):

        ## unique name
        names = set()
        for ds in configs:
            if ds.name in names:
                e = "Data slice names must be unique"
                raise ValueError(e)
            names.add(ds.name)

        ## slice engine
        for ds in configs:
            slice_engine = get_slice(ds.slice_engine)
            data_model = get_model(ds.model)
            pass

        return True

    def _check_content(self, content: Content):

        if content.slice_name not in self._get_slice_names():
            e = f"Invalid data Slice name {content.slice_name}"
            raise ValueError(e)

        data_slice_config = self._get_slice(content.slice_name)
        data_slice = get_slice(data_slice_config.slice_engine)
        if not data_slice.has_field(content.data):
            e = f"no such attribute {content.data} in {data_slice.__name__}"
            raise ValueError(e)

    def _check_spread_sheet_content(self, spread_sheet_content: SpreadSheetContent):

        self._check_content(spread_sheet_content)
        data_slice_config = self._get_slice(spread_sheet_content.slice_name)
        data_slice = get_slice(data_slice_config.slice_engine)
        field = spread_sheet_content.data
        model_field = data_slice.get_field(field)
        if isinstance(spread_sheet_content, SpreadSheetDataFrame):
            if not issubclass(model_field.model, DataModel):
                e = f"Scalar data cannot be used to generate graph"
                raise ValueError(e)
            if spread_sheet_content.projection:
                for project in spread_sheet_content.projection:
                    if not model_field.model.has_field(project):
                        e = f"no such attribute {project} in {model_field.model.__name__}"
                        raise ValueError(e)
        if isinstance(spread_sheet_content, SpreadSheetGraph):
            if not issubclass(model_field.model, DataModel):
                e = f"Scalar data cannot be used to generate graph"
                raise ValueError(e)
            if not model_field.model.has_field(spread_sheet_content.data_field):
                e = f"no such attribute {spread_sheet_content.data_field} in {model_field.model.__name__}"
                raise ValueError(e)
            if not model_field.model.has_field(spread_sheet_content.category_field):
                e = f"no such attribute {spread_sheet_content.category_field} in {model_field.model.__name__}"
                raise ValueError(e)

    def _check_sheet(self, sheeet: Sheet):

        for content in sheeet.content:
            self._check_spread_sheet_content(content)

    def _check_spread_sheet_config(self, spread_sheet: SpreadSheet):

        ## unque sheet names
        titles = set()
        for sheet in spread_sheet.sheets:
            if sheet.title in titles:
                e = "sheet titles with in the spread sheet must be unique"
                raise ValueError(e)
            titles.add(sheet.title)

        for sheet in spread_sheet.sheets:
            self._check_sheet(sheet)

    def _check_file_config(self, file: File):

        if isinstance(file, SpreadSheet):
            self._check_spread_sheet_config(file)

    def _check_item_configs(self, items: list[Item]):

        for item in items:
            if isinstance(item, File):
                self._check_file_config(item)

    def check_report_config(self):

        self._check_data_slice_config(self._report.data_slices)
        self._data_slices = self._report.data_slices
        self._check_item_configs(self._report.items)


class ReportGenerator:

    def __init__(self, report: Report):
        self._report_config = report
        self._data_slices: dict[str, DataSlice] = {}

    @classmethod
    def _evaluate_path(cls, path: TemplateString):
        path = evaluate_template_string(path)
        return str(os.path.abspath(path))

    def _sacalarize(self, data: Iterable[DataModel]):
        scalar_value = ""
        for d in data:
            l = d.to_csv()
            l = [str(i) for i in l]
            scalar_value += "\n" + (":".join(l))
        return scalar_value

    def _process_spread_sheet(self, spread_sheet: SpreadSheet, local_path: str):
        manager = SpreadsheetManager(local_path)
        manager.create_spreadsheet()
        for sheet in spread_sheet.sheets:
            sheet_title = evaluate_template_string(sheet.title)
            manager.add_sheet(sheet_title)
            for content in sheet.content:
                data_slice_ = self._data_slices[content.slice_name]
                data = data_slice_.get(content.data)
                if content.content_type == SpreadSheetContentType.DATA_FRAME:
                    if not isinstance(data, Iterable):
                        data = list(data)
                    if content.projection:
                        headers = [
                            data_slice_._model_type.get_field(p).name
                            for p in content.projection
                        ]
                    else:
                        headers = [
                            m.display_name for m in data_slice_._model_type.fields
                        ]
                    df = [headers]
                    for obj in data:
                        df.append([csv_serializer(e) for e in obj.to_csv(content.projection)])
                    manager.update_sheet(sheet_title, df)
                elif content.content_type == SpreadSheetContentType.GRAPH:
                    if not isinstance(data, Iterable):
                        data = list(data)
                    projection = [content.category_field, content.data_field]
                    field = data_slice_.get_field(content.data)
                    headers = [field.model.get_field(p).name for p in projection]
                    df = [headers]
                    for obj in data:
                        df.append([csv_serializer(e) for e in obj.to_csv(projection)])
                    n_rows = len(df)
                    manager.update_sheet(sheet_title, df)
                    manager.create_graph(
                        sheet_name=sheet_title,
                        chart_type=content.chart_type.value,
                        data_range=f"B2:B{n_rows}",
                        categories_range=f"A2:A{n_rows}",
                        chart_title=content.title,
                    )
                elif content.content_type == SpreadSheetContentType.SCALAR:
                    df = []
                    scalar_title = evaluate_template_string(content.title)
                    if isinstance(data, ScalarType):
                        df = [scalar_title, data]
                    else:
                        if not isinstance(data, Iterable):
                            data = list(data)
                        df = [scalar_title, self._sacalarize(data)]
                    manager.update_sheet(sheet_title, [json_serializer(df)])
        if len(spread_sheet.sheets) > 0:
            manager.delete_sheet("Sheet")

    def _process_custom_file(self, file: File, local_path: str):
        pass

    def _process_file(self, file: File):

        if file.file_type == FileType.ZIP:
            local_path = os.path.join(env.FILES_DIR, f"{str(ID())}.zip")
            if isinstance(file, CustomItem):
                self._process_custom_file(file, local_path)

        if file.file_type == FileType.SPREAD_SHEET:
            local_path = os.path.join(env.FILES_DIR, f"{str(ID())}.xlsx")
            self._process_spread_sheet(file, local_path)

        return {"file_path": local_path}

    def _process_items(self, item):
        if isinstance(item, File):
            file_res = self._process_file(item)
            return {"item": item, "processed": file_res}

    def _share_items(self, drive_config: DriveConfig, processed_items: list[Item]):
        if isinstance(drive_config, GoogleDriveConfig):
            gd = GoogleDrive(google_conn=default_google_conn)
            for processed_item in processed_items:
                try:
                    item = processed_item["item"]
                    processed = processed_item["processed"]
                    if isinstance(item, File):
                        mime_type = "*/*"
                        if item.file_type == FileType.SPREAD_SHEET:
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        if item.file_type == FileType.ZIP:
                            mime_type = "application/zip"
                        path = self._evaluate_path(item.path)
                        filename = os.path.basename(path)
                        local_file = LocalFile(
                            file_path=processed["file_path"],
                            display_name=filename,
                            mime_type=mime_type,
                        )
                        drive_file = gd.upload_file_chunks(local_file)
                        for share in drive_config.share_with:
                            gd.share_access(
                                file=drive_file,
                                email=share.access_to,
                                role=share.access_level,
                            )
                        processed_item["shared"] = {"drive_file": drive_file}
                except: 
                    print(f'Error while sharing {processed_item}')
        return processed_items
    
    def _destruct_items(self, processed_items):
        for processed_item in processed_items: 
            os.remove(processed_item["processed"]["file_path"])

    def generate_report(self):

        ## creation of data slices
        data_to_update = None
        for ds in self._report_config.data_slices:
            data_slice_type_ = get_slice(ds.slice_engine)
            if data_slice_type_ == get_slice(ReportDataSlice.IOCFindingDataSlice):
                if ds.count == DataRange.ALL:
                    data = []
                elif ds.count == DataRange.PREV_DAY:
                    curr = date_from_datetime(curr_time())
                    yestr_day_st = curr-timedelta(days=1)
                    yestr_day_en = curr-timedelta(minutes=1)
                    data = get_iocs(page=1, limit=10**9, date_from=yestr_day_st, date_to=yestr_day_en)
                    data = data["data"]
                else:
                    data = []
                data_to_update = data
            model_data = [data_slice_type_._model_type(d) for d in data]
            self._data_slices[ds.name] = data_slice_type_(model_data)
        print(len(data_to_update))
        ## generation of items in the report
        # self._report_config.items = [self._report_config.items[0]] + [self._report_config.items[2]]
        processed_items = []
        for item in self._report_config.items:
            processed_items.append(self._process_items(item))

        ## sharing generated items using drive configs
        # processed_items = [processed_items[0]] + [processed_items[2]]
        # shared_items = self._share_items(self._report_config.share, processed_items)
        
        # for d in data_to_update:
        #    print(d.id)
        #    _update_shared_reports(d.id, report_id=self._report_config.id)

        # self._destruct_items(processed_items)

        return processed_items
