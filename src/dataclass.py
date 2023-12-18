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
        return URL(self._url)
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
    def hashed(self):
        return hashlib.sha1(self._url.encode("utf-8")).hexdigest()

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


class Contents:
    """
    Contents Unit of Site
    """

    def __init__(self, html):
        self.html = html


@dataclasses.dataclass
class Href:
    """
    element of hrefs in SiteData
    """

    source: URL
    target: URL
    weight: int
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
    contents: str
    hrefs: list[Href]

