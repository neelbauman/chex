"""
Recconaissance Unit
偵察部隊

指定したドメインの構造と詳細を明らかにする。

1. ドメイン以下にあるページの個別の情報を集める
2. ドメイン全体の地図を作成する
3. ページ間の関連・繋がりをフローとして表現する

"""

from bs4 import BeautifulSoup as bs4
import requests

import os, sys, urllib, hashlib
import json, re, datetime, random, collections, dataclasses


@dataclasses.dataclass
class Contents:
    html: str


@dataclasses.dataclass
class Href:
    first: datetime.datetime
    last: datetime.datetime
    active: bool
    n_ref: int
    n_passed: int
    score: float
    url: str


@dataclasses.dataclass
class SiteData:
    """
    Data Unit
    """
    first: datetime.datetime
    last: datetime.datetime
    active: bool
    n_refef: int
    n_visited: int
    hrefs: [Href]
    url: str


class Site(object):
    """
    SiteData & Contents Unit
    """
    def __init__(self, data: SiteData, contents: Contents, *args, **kwargs) -> None:
        self._kwargs = kwargs
        self._args = args
        self.data: SiteData = data
        self.contents: Contents = contents

    def __str__(self):
        return self.data.url

    @property
    def data(self):
        doc = "Site.data property"

        def fget():
            return self._data

        def fset(value):
            try:
                self._data = value
                return True
            except:
                raise ValueError(f"something wrong to set value:{value} for self._data")
                return False

        def fdel():
            try:
                del self._data
                return True
            except:
                raise ValueError("something wrong to delete self._data")

        return property(fget,fset,fdel,doc)

    @property
    def contents(self):
        doc = "Site.contents property"

        def fget():
            return self._contents

        def fset(value):
            try:
                self._contents = value
                return True
            except:
                raise ValueError(f"something wrong to set value:{value} for self._contents")
                return False

        def fdel():
            try:
                del self._contents
                return True
            except:
                raise ValueError(f"something wrong to delete self._contents")

        return property(fget, fset, fdel, doc)


class Crawler(object):
    """
    Survey Unit
    """
    def __init__(self, domain:str, *args, **kwargs):
        self._domain = domain
        self._args = args
        self._kwargs = kwargs
        self._init_index()
        self._init_footprint()

    @property
    def index(self):
        doc = "self.index property"

        def fget(self):
            return self._index
        
        def fset(self, value):
            try:
                self._index = value
                return True
            except:
                raise ValueError(f"something wrong to set value:{value} for self.index")
                return False

        def fdel(self):
            try:
                del self._index
                return True
            except:
                raise ValueError(f"something wrong to delete self.index")

        return property(fget,fset,fdel,doc)

    @property
    def footprint(self):
        doc = "self.footprint property"

        def fget(self):
            return self._footprint
        
        def fset(self, value):
            try:
                self._footprint = value
                return True
            except:
                raise ValueError(f"something wrong to set value:{value} for self.footprint")
                return False

        def fdel(self):
            try:
                del self._footprint
                return True
            except:
                raise ValueError(f"something wrong to delete self.footprint")

        return property(fget,fset,fdel,doc)


    def _url_encode(self, url:str):
        encoded = urllib.parse.quote(url, safe=":/%")

        return encoded

    def _hash_name(self, s:str, extension:str):
        name = hashlib.sha1(s.encode("utf-8")).hexdigest() + extention
        
        return name

    def _init_index(self):
        """
        load or make domain/index.json
        """
        file_name = "index.json"
        dir_name = self._hash_name(self._url_encode(self._domain), extension="")
        index_path = "../tmp/" + dir_name + file_name

        if os.path.exists(index_path):
            index = self.load_json(index_path)
            data_list = [ SiteData(**data) for data in index ]
            self.index = data_list
        else:
            try:
                os.makedirs(dir_name)
            except:
                raise ValueError(f"couldn't make dir:{dir_name}")

            with open(index_path, "w") as f:
                f.write("")

            self.index = []

    def _init_footprint(self) -> None:
        """
        self.indexが空であればSiteData.hrefsから次のtargetを決められないので、
        まずはLPのSiteDataをself.indexに追加する。
        空でなければ、self.indexの中からランダムでスタート地点を決め、
        """
        n = len(self.index)
        if n == 0:
            lp = self._get_lp()
            self.index.append(lp.data)
            self._parent= lp
            self._target = lp
        else:
            r = random.randrange(n)
            data = self.index[r]
            contents = self.get_res(data.url).text
            self._parent = Site(data, contents)
            self._target = Site(data, contents)

        self.footprint = [self._parent.data]

    def _get_target_href(self, algorithm:int = 0):
        """
        現在のself._parent.hrefsの中から適当なアルゴリズムに従ってtarget_hrefを決める
        
        0. hrefsのなかからランダムな選択
        1. 頻度の少ないものから。候補が複数ある場合はランダム
        """
        # case文で実装
        if algoritm == 0:
            hrefs = self._parent.hrefs
            n = len(hrefs)

            if n < 1:
                raise ValueError("couldn't get next_target")
            else:
                r = random.randrange(n)

            target_href = hrefs[r]

        self._target_href = target_href

        return target_href

    def _update_target_href(self, res):
        if res.status_code == 200:
            self._target_href.active = True
            self._target_href.n_passed += 1
            self._target_href.last = res["Date"]

            return True
        
        else:
            return False
            raise ValueError("it seems that request has been failed")

    def _update_hrefs(self):
        pass


    def _get_target_data(self, target_href):
        """
        search the target in self.index which has the same url as target_href.url
        """

        candidate = [ data for data in self.index if data.url == target_href.url ]
        
        if len(candidate) == 0:
            next_target_data = None

        elif len(candidate) >= 2:
            next_target_data = None
            raise ValueError("there is some duplication in self.index")
        else:
            next_target_data = candidate[0]
            self._target_i = self.index.index(next_target_data)

        return next_target_data

    def _get_target(self, next_target_data):
        if next_target_data == None:
            return None

        res = self.get_res(next_target_data.url)
        data, contents = self._get_data_and_contents(res)
        site = Site(data, contents)
        
        self._target = site

        return site

    def _get_lp(self) -> Site:
        """
        get LP which is a page that is redirected from server root like https://math.jp
        """
        res = self.get_res(self._domain)
        lp_data, lp_contents = self._get_data_and_contents(res)
        lp = Site(lp_data, lp_contents)

        self._lp_url = lp.data.url

        return lp


    def load_json(self, file_path):
        try:
            with open(file_path, "r") as f:
                s = f.read()
            data = json.loads(s)
        except:
            data = None
            raise ValueError(f"couldn't load json:{file_path}")

        return data

    def get_res(self, url:str, **kwargs) -> requests.Response:
        url = self._url_encode(url)
        params = kwargs if kwargs else None

        try:
            res = requests.get(url, params=params)
        except:
            raise ValueError(f"Request Failed. Couldn't get from {url}")

        return res

    def _get_soup(self, res):
        soup = bs4(res.content, "html.parser")

        return soup

    def _get_hrefs(self, soup, startswith="/wiki/"):
        a_list = soup.find_all("a")
        hrefs = [ a.get("href") for a in a_list if a.get("href").startswith(startswith) ]

        return hrefs

    def _get_data_and_contents(self, res:requests.Response) -> (SiteData, Contents):
        soup = self._get_soup(res)
        hrefs = self._get_hrefs(soup)
        hist = collections.Counter(hrefs).most_common()
        
        hrefs = [{
            "first": "yet",
            "last": "yet",
            "active": True,
            "n_ref": href[1],
            "n_passed": 0,
            "score": 0,
            "url": self._url_encode(domain+href[0]),
            }
            for href in hist ]

        data = {
            "first": "yet",
            "last": "yet",
            "active": True,
            "n_refed": 0,
            "n_visited": 0,
            "hrefs": hrefs,
            "url": self._url_encode(res.url),
            }

        contents = {
            "html": res.text
        }

        return SiteData(**data), Contents(**text)


