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
class HrefList:
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
    hrefs: [HrefList]
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
        self._get_started()

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
        対象のドメインのindex.jsonがあればそれをロードする。
        なければディレクトリごとindex.jsonを作成して、自分は空listを持つ。
        """
        file_name = "index.json"
        dir_name = self._hash_name(self._url_encode(self._domain), extension="")
        index_path = "../tmp/" + dir_name + file_name

        if os.path.exists(index_path):
            index = self.load_json(index_path)
            data_list = []
            for data in index:
               data_list.append(SiteData(**data))

            self.index = data_list
        else:
            try:
                os.makedirs(dir_name)
            except:
                raise valueError(f"couldn't make dir:{dir_name}")

            with open(index_path, "w") as f:
                f.write("")
            self.index = []
    
    def _get_lp(self) -> SiteData:
        """
        サーバールートからリダイレクトされるページ(LP)の取得
        """
        res = self.get_res(self._domain)
        lp = self._get_data_from_res(res)

        self._lp_url = lp.url

        return lp

    def _get_started(self):
        """
        self.index:[SiteData]が空であればSiteData.hrefsから次のtargetを決められないので、
        まずはLPのSiteDataをself.indexに追加する。
        空でなければ、self.indexの中からランダムでスタート地点を決め、
        スタート地点のhrefsから次のターゲットをアルゴリズムに従って選定する。
        """
        n = len(self.index)
        if n == 0:
            data = self._get_lp()
            self.index.append(data)
        else:
            r = random.randrange(n)
            data = self.index[r]

        self._target = data
        self.footprint = [data.url]
        self._next_target_url = self._get_next_target_url()

    def _get_next_target_url(self, algorithm:int = 0) -> str:
        """
        現在のself._target.hrefsの中から適当なアルゴリズムに従ってself._next_targetを決める。
        
        0. hrefsのなかからランダムな選択
        # 1. 頻度の少ないものから。候補が複数ある場合はランダム
        """
        if algoritm == 0:
            hrefs = self._target.hrefs
            n = len(hrefs)

            if n < 1:
                raise ValueError("couldn't get next_target")
            else:
                r = random.randrange(n)

            next_target_url = hrefs[r].url

        return next_target_url

    def load_json(self, file_path):
        try:
            with open(file_path, "r") as f:
                s = f.read()
            data = json.loads(s)
        except:
            data = None
            raise ValueError(f"couldn't load json:{file_path}")

        return data

    def get_res(self, url:str, **kwargs):
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

    def get_json_from_res(self, res):
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
        
        return data

    def _get_data_from_res(self, res):
        json_dict = self.get_json_from_res(res)
        data = SiteData(**json_dict)

        return data
        

