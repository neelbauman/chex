"""
Recconaissance Unit

指定したドメインの構造と詳細を明らかにする。

1. ドメイン以下にあるページの個別の情報を集める
2. ドメイン全体の地図を作成する
3. ページ間の関連・繋がりをフローとして表現する

"""

from bs4 import BeautifulSoup as bs4
import requests

import os, sys, urllib, hashlib
import json, re, datetime, time, random, collections, dataclasses


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
            self._data = value

        def fdel():
            try:
                del self._data
                return True
            except:
                raise ValueError("something wrong to delete self._data")

        return property(fget,fset,fdel,doc)
    @data.setter
    def data(self, value):
        self._data = value

    @property
    def contents(self):
        doc = "Site.contents property"

        def fget():
            return self._contents

        def fset(value):
            self._contents = value

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
        return self._index
    @index.setter
    def index(self, value):
        self._index = value

    @property
    def footprint(self):
        doc = "self.footprint property"

        def fget(self):
            return self._footprint
        
        def fset(self, value):
            try:
                self._footprint = value
            except:
                raise ValueError(f"something wrong to set value:{value} for self.footprint")

        def fdel(self):
            try:
                del self._footprint
            except:
                raise ValueError(f"something wrong to delete self.footprint")

        return property(fget,fset,fdel,doc)


    def _url_encode(self, url:str):
        encoded = urllib.parse.quote(url, safe=":/%")

        return encoded

    def _hash_name(self, s:str, extension:str):
        name = hashlib.sha1(s.encode("utf-8")).hexdigest() + extension
        
        return name

    def _init_index(self):
        """
        load or make domain/index.json
        """
        base_name = "../tmp/"
        file_name = "/index.json"
        dir_name = base_name + self._hash_name(self._url_encode(self._domain), extension="")
        index_path = dir_name + file_name

        if os.path.exists(index_path):
            index = self.load_json(index_path)

            if index:
                data_list = [ SiteData(**data) for data in index ]
                self.index = data_list
            else:
                self.index = []
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
            self._p_i = 0
            self._i = 0
        else:
            r = random.randrange(n)
            data = self.index[r]
            contents = self.get_res(data.url).text
            self._parent = Site(data, contents)
            self._target = Site(data, contents)
            self._p_i = r
            self._i = r

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

    def _update_target_href(self):
        loop = 1
        while loop < 100:
            res = self.get_res(self._target_href.url)
            if res.status_code == 200:
                self._target_href.active = True
                self._target_href.n_passed += 1
                self._target_href.last = res["Date"]
                break
            else:
                self._target_href.active = False
                self._target_href = self._get_target_href()
                loop += 1
        else:
            raise ValueError("something is wrong")

        self._res = res


    def _get_target_data(self):
        """
        search the target in self.index which has the same url as self._target_href.url
        """

        candidate = [ data for data in self.index if data.url == self._target_href.url ]
        
        if len(candidate) == 0:
            target_data = None
            self._i = -1

        elif len(candidate) >= 2:
            target_data = None
            raise ValueError("there is some duplication in self.index")
        else:
            target_data = candidate[0]
            self._i = self.index.index(target_data)

        self._data = target_data

        return target_data

    def _update_target_data(self):
        data, contents = self._get_data_and_contents(self._res)

        if self._data:
            data = self._data

        site = Site(data, contents)
        site.data.n_visited += 1
        site.data.active = True
        site.data.last = self._res["Date"]
        
        self._target = site

        return site

    def _update_index(self):
        self.index[self._p_i] = self._parent.data
        if self._i == -1:
            self.index.append(self._target.data)
        else:
            self.index[self._i] = self._target.data

        self._parent = self._target
        self._p_i = self._i

    def _update_footprint(self):
        self.footprint.append(self._target.data)

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

        return data

    def dump_json(self, file_path):
        json_list = [ dataclassed.asdict(data) for data in seif.index ]
        try:
            with open(file_path, "w") as f:
                json.dump(json_list, f, indent=4)
        except:
            raise ValueError("some error with dump self.index")


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

    def crawling(self, interval=1):
        """
        interval is the time(s) to wait to make a next request 
        """
        loop = True
        while loop:
            self._get_target_href()
            self._update_target_href()
            self._get_target_data()
            self._update_target_data()
            self._update_index()
            self._update_footprint()
            time.sleep(interval)
            if len(self._index) >= 100:
                loop = False
            else:
                loop = True
        else:
            self.dump_json("tmp/test.json")


            


            

            



