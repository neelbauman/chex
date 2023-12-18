import dataclasses
import datetime
import urllib, hashlib


class URL:
    def __init__(self, url: str):
        self.url = url

    def __eq__(self, other):
        if type(self) == type(other):
            return self.url == other.url
        else:
            raise NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.__str__()

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
        return urllib.parse.quote(self._url, safe=":/%")

    @property
    def decoded(self):
        return urllib.parse.unquote(self._url)

    @property
    def hashed(self):
        return hashlib.sha1(self._url.encode("utf-8")).hexdigest()


@dataclasses.dataclass
class Contents:
    """
    Contents Unit of Site
    """

    html: str | None
    contents: bytes | None


@dataclasses.dataclass
class Href:
    """
    element of hrefs in SiteData
    """

    source: URL
    target: URL
    firstPass: datetime.datetime
    lastPass: datetime.datetime
    passNumber: int
    isActive: bool
    score: float


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
    contents: Contents
    hrefs: list[Href]


