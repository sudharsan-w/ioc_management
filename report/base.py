from dataclasses import dataclass
from typing import Generic, TypeVar, Union, Iterable

T = TypeVar("T")
ScalarType = Union[str, int, float]


@dataclass
class Field:
    name: str
    display_name: str
    description: str

    def __eq__(self, value):
        if isinstance(value, str):
            return self.name == value
        if isinstance(value, Field):
            return self.name == value.name
        return False

    def __hash__(self):
        return str.__hash__(self.name)

    def __str__(self):
        return self.name

    @property
    def __dict__(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
        }


class DataModel(Generic[T]):
    fields: list[Field]
    _fields_dict: dict[str, Field] = None
    _source_type: T = T

    def __init__(self, data: T):
        if type(self) == DataModel.__name__:
            e = f"cannot create object of {DataModel.__name__}"
            raise ValueError(e)
        if not hasattr(self, "fields"):
            e = f"fields attribute not set in {type(self).__name__}"
            raise AttributeError(e)
        self._check_all_fields()
        self._data = data

    def _check_all_fields(self):
        for field in self.fields:
            if field.name not in self.__dir__():
                e = f"no such property {field.name} in {type(self).__name__}"
                raise AttributeError(e)

    @classmethod
    def _get_fields(cls):
        if not cls._fields_dict:
            cls._fields_dict = {f.name: f for f in cls.fields}
        return cls._fields_dict

    @classmethod
    def get_fields(cls) -> dict[Field]:
        return cls._get_fields()

    @classmethod
    def get_field(cls, key: str) -> Union[Field]:
        if cls.has_field(key):
            return cls._get_fields()[key]
        return None

    @classmethod
    def has_field(cls, field: Union[Field]):
        return field in cls.fields

    def _get(self, key: Union[str, Field]):
        if self.has_field(key):
            if isinstance(key, Field):
                return self.__getattribute__(key.name)
            return self.__getattribute__(key)
        return None

    def get(self, key: Union[str, Field], default_=None):
        if not self._get(key):
            return default_
        return self._get(key)

    def __getitem__(self, key: Union[str, Field]):
        if not self._get(key):
            e = f"no such key {key} in {type(self).__name__}"
            raise KeyError(e)
        return self._get(key)

    @property
    def __dict__(self):
        dict_ = {}
        for name, _ in self._get_fields.items():
            dict_[name] = self.__getattribute__(name)
        return dict_

    def to_csv(self, projection: list[Union[Field, str]] = None):
        if not projection:
            projection = self.fields
        row = []
        for field in projection:
            if isinstance(field, Field):
                row.append(self.__getattribute__(field.name))
            else:
                row.append(self.__getattribute__(field))
        return row


@dataclass
class Analytics:
    name: str
    display_name: str
    description: str
    model: Union[DataModel, list[DataModel], ScalarType]

    def __eq__(self, value):
        if isinstance(value, str):
            return self.name == value
        if isinstance(value, Analytics):
            return self.name == value.name
        return False

    def __hash__(self):
        return str.__hash__(self.name)

    def __str__(self):
        return self.name

    @property
    def __dict__(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "model": self.model,
        }


class DataSlice(Generic[T]):
    analytics: list[Analytics]
    _analytics_dict: dict[str, Analytics] = None
    _model_type: T = T

    def __init__(self, data: Iterable[T] = []):
        if type(self) == DataSlice.__name__:
            e = f"cannot create object of {DataSlice.__name__}"
            raise ValueError(e)
        if not hasattr(self, "analytics"):
            e = f"fields attribute not set in {type(self).__name__}"
            raise AttributeError(e)
        self._check_all_fields()
        self._data = data

    def _check_all_fields(self):
        for field in self.analytics:
            if field.name not in self.__dir__():
                e = f"no such property {field.name} in {type(self).__name__}"
                raise AttributeError(e)

    @classmethod
    def _get_fields(cls):
        if not cls._analytics_dict:
            cls._analytics_dict = {a.name: a for a in cls.analytics}
        return cls._analytics_dict

    @classmethod
    def get_fields(cls) -> dict[Analytics]:
        return cls._get_fields()

    @classmethod
    def get_field(cls, key: str) -> Analytics:
        if cls.has_field(key):
            return cls._get_fields()[key]
        return None

    @classmethod
    def has_field(cls, field: Union[str, Analytics]):
        return field in cls.analytics

    @classmethod
    def supports_type(cls, obj: object):
        return isinstance(obj, cls._model_type)

    def _get(self, key: Union[str, Analytics]):
        if self.has_field(key):
            if isinstance(key, Analytics):
                return self.__getattribute__(key.name)
            return self.__getattribute__(key)
        return None

    def get(self, key: Union[str, Analytics]):
        return self._get(key)

    def __getitem__(self, key: Union[str, Analytics]):
        if not self._get(key):
            e = f"no such key {key} in {type(self).__name__}"
            raise KeyError(e)
        return self._get(key)

    @property
    def __dict__(self):
        dict_ = {}
        for name, _ in self._get_fields().items():
            dict_[name] = self.__getattribute__(name)
        return dict_

