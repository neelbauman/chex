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

import hashlib
import json, re, collections, urllib, hashlib

class Crawler(object):
    """
    Reconnaissance　Unit

    domainを指定して初期化したら、そのドメインのindexを探す。
    """

    def __init__(self, domain:str, *args, **kwargs):
        self._domain = domain
        self.page_index = {}

    def _get_lp(self):
        """
        サーバールートにアクセスした際にリダイレクトされるページのURL
        """
        res = self.get_res("")
        lp_url = res.url
        self._lp_url = lp_url

        return lp_url

    def get_res(self, target:str, **kwargs):
        domain = self._domain
        params = kwargs if kwargs else None

        try:
            res = requests.get(domain+target, params=params)
        except:
            raise ValueError("Request Failed")

        self.page_index.add(domain+target)

        return res

    def load(self, file_path):
        try:
            with open(file_path, "r") as f:
                s = f.read()
            data = json.loads(s)
        except:
            data = None

        return data

    def _make_soup(self, res):
        soup = bs4(res.content, "html.parser")

        return soup

    def _get_hrefs(self, soup, startswith="/wiki/"):
        a_list = soup.find_all("a")
        hrefs = [ a.get("href") for a in a_list if a.get("href").startswith(startswith) ]

        return hrefs

    def get_json(self, res):
        soup = self._make_soup(res)
        hrefs = self._get_hrefs(soup)
        hist = collections.Counter(hrefs).most_common()
        
        hrefs = [{
            "profile": {
                "first": "yet",
                "last": "yet",
                "active": True,
                },
            "number": href[1],
            "visited": 0,
            "score": 0,
            "url": href[0],
            }
            for href in hist ]

        data = {
            "url": res.url,
            "first": "yet",
            "last": "yet",
            "count": 0,
            "hrefs": hrefs,
            "content": str(soup.select("html")[0]),
            "edited": False,
            }
        
        return data
        




