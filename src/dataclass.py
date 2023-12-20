import dataclasses
import datetime
import re
import urllib, hashlib


class URL(str):
    def __init__(self, url: str = ""):
        self.url = url

    def __eq__(self, other):
        if type(self) == type(other):
            return self.url == other.url
        else:
            raise NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        raise NotImplemented

    def __gt__(self, other):
        raise NotImplemented

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __str__(self):
        return self.url

    def __repr__(self):
        return super().__repr__()

    @property
    def url(self):
        return self._url
    @url.setter
    def url(self, value):
        decoded = urllib.parse.unquote(value)
        if value == decoded:
            self._url = value
        else:
            self._url = decoded

    @property
    def encoded(self):
        url = urllib.parse.quote(self._url, safe=":/%")
        return URL(url)

    @property
    def domain(self):
        match = re.search(r"([a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}/", self.url)
        domain = match.group()

        return URL(domain)

    @property
    def protocol(self):
        match = re.search(r"^https?://", self.url)
        protocol = match.group()

        return URL(protocol)

    @property
    def hashed(self) -> str:
        return hashlib.sha1(self._url.encode("utf-8")).hexdigest()


class Contents:
    """
    Contents Unit of Site
    """

    def __init__(self, html):
        self.html = html


@dataclasses.dataclass
class Href:
    """
    response to Edge of index.G
    """

    source: URL
    target: URL
    weight: int = 1
    score: float = 0.0
    isActive: bool = False
    timestamp: datetime.datetime | None = dataclasses.field(init=False)

    def __post_init__(self):
        """
        init時、activeならinit時の時刻をtimestampとする。
        not activeならtimestampはNone。
        """
        if self.isActive:
            self.timestamp = datetime.datetime.now()
        else:
            self.timestamp = None

    @property
    def attr_dict(self):
        return {
            "weight": self.weight,
            "score": self.score,
            "isActive": self.isActive,
            "timestamp": self.timestamp,
        }

    def asEdge(self):
        return (self.source, self.target, self.attrs(),)

    def activate(self):
        self.timestamp = datetime.datetime.now()
        self.isActive = True

    def deactivate(self):
        self.timestamp = datetime.datetime.now()
        self.isActive = False


@dataclasses.dataclass
class Site:
    """
    MetaData Unit Of Site
    """

    url: URL
    firstVisit: datetime.datetime
    lastVisit: datetime.datetime
    visitNumber: int
    isActive: bool
    score: float
    contents: str
    hrefs: list[Href]

