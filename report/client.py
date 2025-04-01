import json
from typing import Iterable

from .base import DataModel, DataSlice, Field, Analytics, ScalarType
from models import IOCFinding


class IOCFindingRecord(DataModel[IOCFinding]):
    _source_type = IOCFinding

    fields = (
        Field(name="id", display_name="id", description=""),
        Field(name="source", display_name="Source Document", description=""),
        Field(name="iocs", display_name="IOCS", description=""),
        Field(name="found_at", display_name="Found At", description=""),
        Field(name="iocs_breakdown", display_name="IOCs Breakdown", description=""),
    )

    @property
    def id(self):
        return self._data.id

    @property
    def source(self):
        if self._data.source_ref:
            return self._data.source_ref.key

    @property
    def iocs(self):
        for k, val in self._data.keys.items():
            if not isinstance(val, list):
                self._data.keys[k] = [val]
        return self._data.keys

    @property
    def iocs_breakdown(self):
        iocs = self.iocs
        return {k: len(iocs[k]) for k in iocs}
    
    @property
    def found_at(self):
        return self._data.created_at


class IOCFindingDataSlice(DataSlice[IOCFindingRecord]):
    _model_type = IOCFindingRecord

    class IOCTypeCount(DataModel[dict]):
        fields = (
            Field(name="ioc_type", display_name="IOC Type", description=""),
            Field(name="count", display_name="Count", description=""),
        )

        @property
        def ioc_type(self):
            return self._data["type"]

        @property
        def count(self):
            return self._data["count"]

    class IOCCount(DataModel[dict]):
        fields = (
            Field(name="ioc", display_name="IOC", description=""),
            Field(name="count", display_name="Count", description=""),
        )

        @property
        def ioc(self):
            return self._data["ioc"]

        @property
        def count(self):
            return self._data["count"]

    class SourceCount(DataModel[dict]):
        fields = (
            Field(name="source", display_name="IOC", description=""),
            Field(name="count", display_name="Count", description=""),
        )

        @property
        def source(self):
            return self._data["source"]

        @property
        def count(self):
            return self._data["count"]

    analytics = (
        Analytics(
            name="ioc_type_breakdown",
            display_name="IOC Type Breakdown",
            description="",
            model=IOCTypeCount,
        ),
        Analytics(
            name="total_iocs",
            display_name="Totoal IOCs",
            description="",
            model=ScalarType,
        ),
        Analytics(
            name="unique_iocs",
            display_name="Unique IOCs",
            description="",
            model=ScalarType,
        ),
        Analytics(
            name="iocs_breakdown",
            display_name="IOCs breakdown",
            description="",
            model=IOCCount,
        ),
        Analytics(
            name="source_breakdown",
            display_name="Source Breakdown",
            description="",
            model=SourceCount,
        ),
        Analytics(
            name="all", display_name="all", description="", model=IOCFindingRecord
        ),
    )

    @property
    def all(self):
        return self._data

    @property
    def ioc_type_breakdown(self, top=10) -> Iterable[IOCTypeCount]:
        freq: dict[str, int] = {}
        for ioc_find in self._data:
            for k, val in ioc_find.iocs_breakdown.items():
                freq[str(k)] = freq.get(str(k), 0) + val
        sorted_by_freq = sorted(list(freq.items()), key=lambda u: u[1], reverse=True)
        unique_types = len(sorted_by_freq)
        return list(
            map(
                lambda u: self.IOCTypeCount({"type": u[0], "count": u[1]}),
                sorted_by_freq[: min(unique_types, top)],
            )
        )

    @property
    def total_iocs(self):
        total = 0
        for ioc_find in self._data:
            for k, val in ioc_find.iocs_breakdown.items():
                total += val

        return total

    @property
    def unique_iocs(self):
        iocs = set()
        for ioc_find in self._data:
            for _, val in ioc_find.iocs.items():
                iocs.update(val)
        return len(iocs)

    @property
    def iocs_breakdown(self, top=5) -> Iterable[IOCCount]:
        freq: dict[str, int] = {}
        for ioc_find in self._data:
            for _, val in ioc_find.iocs.items():
                for e in val:
                    freq[str(e)] = freq.get(str(e), 0) + 1
        sorted_by_freq = sorted(list(freq.items()), key=lambda u: u[1], reverse=True)
        unique_types = len(sorted_by_freq)
        return list(
            map(
                lambda u: self.IOCCount({"ioc": u[0], "count": u[1]}),
                sorted_by_freq[: min(unique_types, top)],
            )
        )

    @property
    def source_breakdown(self, top=5) -> Iterable[SourceCount]:
        freq: dict[str, int] = {}
        for ioc_find in self._data:
            if not ioc_find.source:
                continue
            freq[ioc_find.source] = freq.get(ioc_find.source, 0) + 1
        sorted_by_freq = sorted(list(freq.items()), key=lambda u: u[1], reverse=True)
        unique_types = len(sorted_by_freq)
        return list(
            map(
                lambda u: self.SourceCount({"source": u[0], "count": u[1]}),
                sorted_by_freq[: min(unique_types, top)],
            )
        )
