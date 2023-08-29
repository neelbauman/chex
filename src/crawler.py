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

import os, sys
import json, re, collections, urllib, hashlib, random


class Site(object):
    """
    Data Unit
    """
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self.data = None
        self.contents = requests.Response()

    def __str__(self):
        return self.data["url"]

    def dumps_data(self):
        return 

    @property
    def data(self):
        doc = "data property"

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


class Crawler(object):
    """
    Survey Unit
    """
    def __init__(self, domain:str, *args, **kwargs):
        self._domain = domain
        self._args = args
        self._kwargs = kwargs
        self._target = ""
        self._i_t = 0
        self._next_target = ""
        self._i_nt = 0
        self._footprint = []
        self._init_index(domain)
        self._get_started()

    def _url_encode(self, url:str):
        encoded = urllib.parse.quote(url, safe=":/%")

        return encoded

    def _hash_name(self, s:str, extension:str):
        name = hashlib.sha1(s.encode("utf-8")).hexdigest() + extention
        
        return name

    def _init_index(self, domain):
        file_name = "index.json"
        dir_name = "../tmp/" + self._hash_name(self._url_encode(domain), "")
        index_path = dir_name + file_name

        self._dir_name = dir_name

        if os.path.exists(index_path):
            with open(index_path, "r") as f:
                s = f.read()
            index = json.loads(s)
            self._index = index
        else:
            os.makedirs(dir_name)
            with open(index_path, "w") as f:
                f.write("")
            self._index = []

    def _get_lp(self):
        """
        サーバールートからリダイレクトされるページ(LP)の取得
        """
        res = self.get_res(self._domain)
        data = self.get_json_from_res(res)
        lp_url = res.url
        self._lp_url = lp_url

        return lp_url, data

    def _get_started(self):
        n = len(self._index)
        if n == 0:
            lp_url, lp_data = self._get_lp()
            self._index.append(lp_data)
            self._target = lp_url
            self._footprint.append(lp_url)
        else:
            r = random.randrange(n)
            data = self._index[r]
            res = self.get_res(data["url"])
            data = self.get_json_from_res(res)

    def _next_target(self):
        try:
            i = self._index.index(self._target)
        except:
            raise ValueError("現在のtargetのindexが取得できません。")
        
        hrefs = self._index[i]["hrefs"]
        n = len(hrefs)

        if n < 1:
            raise ValueError("遷移先の候補がもうありません。")
        else:
            r = random.randrange(n)

        while target == next_target:
            r = random.randrange(n)
            if self._index[r][
            next_target = self._index[r]["url"]
            

    def load(self, file_path):
        try:
            with open(file_path, "r") as f:
                s = f.read()
            data = json.loads(s)
        except:
            data = None

        return data

    def get_res(self, target:str, **kwargs):
        target = self._url_encode(target)
        params = kwargs if kwargs else None

        try:
            res = requests.get(target, params=params)
        except:
            raise ValueError("Request Failed")

        self._target = target
        self._footprint.append(target)

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

    def get_json_from_target(self, target):
        res = self.get_res(target)
        data = slef.get_json_from_res(res)

        return data
        




