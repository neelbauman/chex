from typing import Any
import dataclasses
from datetime import datetime

from src.datatype.collections import nodetuple, edgetuple

@dataclasses.dataclass
class Site:
    """
    correspond to Node of Graph
    """
    url: str
    isActive: bool = True
    value: float = 0.0
    group: str|None = None
    first: datetime|None = None
    last: datetime|None = None
    timestamp: datetime|None = None
    _strftime_fmt: str = "%Y-%m-%dT%H:%M:%S.%f+09:00"
    _id: int = dataclasses.field(init=False)

    @property
    def id(self):
        return self._id
    @property
    def strftime_fmt(self):
        return self._strftime_fmt

    def __str__(self):
        return self.url

    def __repr__(self):
        return f"<Site {self.__str__()} at 0x{id(self):x}>"

    def __hash__(self):
        return hash(self.__str__())

    def __lt__(self, other):
        try:
            return self.timestamp < other.timestamp
        except Exception as e:
            raise NotImplemented

    def __gt__(self, other):
        try:
            return self.timestamp > other.timestamp
        except Exception as e:
            raise NotImplemented

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)
    
    def __post_init__(self):
        self._id = self.__hash__()
        self.first= self.first or datetime.now()
        self.last = self.last or self.first
        self.timestamp = self.timestamp or self.first

    def touch(self):
        self.last = self.timestamp
        self.timestamp = datetime.now()

    def activate(self):
        self.isActive = True
        self.touch()
        return self

    def deactivate(self):
        self.isActive = False
        self.touch()
        return self

    def _dict_factory(self, items: [ (str, Any) ]) -> { str: Any }:
        adict = {}
        for key, value in items:
            if key.startswith("_"):
                continue
            else:
                adict[key] = value
        return adict

    def asDict(self):
        adict = dataclasses.asdict(self, dict_factory=self._dict_factory)
        return adict

    def asNode(self, key: str = "url"):
        adict = self.asDict()
        kv = adict.pop(key)
        return nodetuple(kv, adict)

    def _dict_serialize(self, items: [ (str, Any) ]) -> { str: Any }:
        adict = {}
        for key, value in items:
            if key.startswith("_"):
                continue
            elif type(value) is datetime:
                adict[key] = value.strftime(self.strftime_fmt)
            elif type(value) in (int, float, str, bool, None):
                adict[key] = value
            else:
                adict[key] = str(value)
        return adict

    def asSerializedDict(self, name: str, key: str):
        adict = dataclasses.asdict(self, dict_factory=self._dict_serialize)
        id_value = adict.pop(key)
        adict[name] = id_value
        return adict


@dataclasses.dataclass
class Href:
    """
    correspond to Edge of Graph
    """

    source: Site
    target: Site
    isActive: bool = True
    weight: int = 1
    score: float = 0.0
    _id: str = dataclasses.field(init=False)

    @property
    def id(self):
        return self._id

    def __str__(self):
        return str(self.source)+" -> "+str(self.target)

    def __repr__(self):
        return f"<Href {self.__str__()} at {id(self)}>"

    def __hash__(self):
        return hash(self.__str__())

    def __post_init__(self):
        self._id = self.__hash__()

    def _dict_factory(self, items: [ (str, Any) ]) -> { str: Any }:
        adict = {}
        for key, value in items:
            if key.startswith("_"):
                continue
            else:
                adict[key] = value
        return adict

    def asDict(self):
        adict = dataclasses.asdict(self, dict_factory=self._dict_factory)
        return adict

    def asEdge(self, key: str = "url"):
        adict = self.asDict()
        source = adict.pop("source")
        target = adict.pop("target")
        return edgetuple(source[key], target[key], adict)

    def activate(self):
        self.timestamp = datetime.now()
        self.isActive = True
        return self

    def deactivate(self):
        self.timestamp = datetime.now()
        self.isActive = False
        return self

