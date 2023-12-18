"""
Recconaissance Unit
"""

import requests
from requests.exceptions import Timeout
from requests.models import Response

from bs4 import BeautifulSoup as bs4

import os, sys
import json
import re
import time
import random
import collections
import urllib, hashlib
from datetime import timedelta, datetime

from dataclass import URL, Href, Contents, Site


class IndexData():
    def __init__(
        self,
        filepath: str | None = None,
    ):
        self.filepath = filepath

        try:
            self.loadJson()
        except:
            self.json = []
            self.dumpJson()

    @property
    def filepath(self):
        return self._filepath
    @filepath.setter
    def filepath(self, value: str):
        self._filepath = value

    @property
    def dirname(self):
        if self.filepath:
            return os.path.dirname(self.filepath)
        else:
            return None

    @property
    def filename(self):
        if self.filepath:
            return os.path.basename(self.filepath)
        else:
            return None
        
    def loadJson(self, filepath: str | None = None):
        path = filepath if filepath else self.filepath
        with open(path, "r") as f:
            s = f.read()

        data = json.loads(s)
        self.json = data

    def dumpJson(self, filepath: str | None = None):
        path = filepath if filepath else self.filepath
        try:
            os.makedirs(self.dirname)
        except Exception as e:
            pass
        finally:
            with open(filepath, "w") as f:
                json.dump(self.json, f, indent=4)

    def _update_index(self, interval=5) -> None:
        """
        """
        loop = 0
        while loop < 100:
            self._select_target_href(algorithm=0)
            try:
                time.sleep(interval)
                res = self._get_res(self._target_href.url)
            except Timeout as e:
                loop += 1
                continue
                
            if res.status_code == 200:
                break
            else:
                self._target_href.active = False
                if self._data:
                    self._data.active = False
                loop += 1
                continue
        else:
            raise ValueError(f"couldn't success in getting response from {self.domain}")

        data, contents = self._get_data_and_contents(res)

        # update self._target_href
        if self._target_href.last == "yet":
            self._target_href.first = res.headers["Date"]
        self._target_href.active = True
        self._target_href.n_passed += 1
        self._target_href.last = res.headers["Date"]

        # update self._data
        self._select_target_data()
        if self._data is not None:
            self._data.active = True
            self._data.n_visited += 1
            self._data.last = res.headers["Date"]
        else:
            self._data = data
            self.index.append(self._data)

        self._target = Site(self._data, contents)


class Footprint():
    def __init__(self, res = None, *args, **kwargs):
        self.hist = []
        if res:
            self.add(res)

    def add(self, res):
        self.hist = [*self.hist, *res if type(res) is list else res ]

    def _update_footprint(self) -> None:
        self.footprint.append(self._target.data)
        self._parent = self._target


class Crawler():
    """
    Survey Unit
    """
    base_dir = "tmp"

    def __init__(
        self,
        url: str | None = None,
        domain: str | None = None,
        filename: str = "index.json"
        *args,
        **kwargs
    ):
        if url:
            self.url = URL(url).decoded
            self.domain = self.url.domain.decoded
        elif domain:
            res = self._get_res(domain)
            self.domain = URL(domain).decoded
            self.url = URL(res.url).decoded
        else:
            raise NotImplemented

        self._init_index(filename)
        self._init_footprint()
    
    @property
    def domain(self):
        return self._domain
    @domain.setter
    def domain(self, value):
        self._domain = value

    @property
    def index(self):
        return self._index
    @index.setter
    def index(self, value):
        self._index = value

    @property
    def footprint(self):
        return self._footprint
    @footprint.setter
    def footprint(self, value):
        self._footprint = value


    def _init_index(self, filename):
        indexpath = os.path.join(self.base_dir, self.domain.hashed, filename)
        self.index = IndexData(indexpath)

    def _init_footprint(self):
        r = random.randrange(len(self.index.json))

        if r == 0:
            res = self._get_res(self.url.encoded)
        else:
            res = self._get_res(self.index.json[r].url.encoded)

        self.footprint = Footprint(res)

    def _select_target_href(self, algorithm:int = 0):
        hrefs = self._parent.hrefs
        n = len(hrefs)
        if n < 1:
            raise ValueError("couldn't get next_target")

        if algorithm == 0:
            r = random.randrange(n)
        elif algorithm == 1:
           yets = [ (i, href) for i, href in enumerate(hrefs) if href.n_passed == 0 ]
           if len(yets) == 0:
               r = random.randrange(n)
           else:
               q = random.randrange(len(yets))
               r = yets[q][0]
        else:
            raise ValueError("Please input valid algorithm No.")

        self._target_href = hrefs[r]

    def _select_target_data(self):
        cand = [ data for data in self.index if data.url == self._target_href.url ]
        if len(cand) >= 2:
            print(self._parent.data.url)
            print(self._target_href.url)
            raise ValueError("indexに重複がある")
        elif len(cand) == 1:
            self._data = cand[0]
            # cand[0]がNoneを返している可能性
            # 2重にappendしている可能性
        else:
            self._data = None
        """
        # 以下のコードではindexの一意性が担保されなかった。
        try:
            # check if self._target_href exists in self.index,
            # and then get the index if exists.
            i = self.index.index(self._target_href)
        except ValueError as e:
            # if not exists
            self._data = None
        else:
            # if exists
            self._data = self.index[i]
        """

    def _get_res(self, url: URL, n_try: int = 10, **kwargs) -> requests.models.Response | None:
        """
        if get returns Timeout, try 10 times anothor.
        if those failed, then raise Timeout for the first time.
        """
        url = url.encoded
        params = kwargs if kwargs else None

        for loop in range(n_try):
            try:
                res = requests.get(url, timeout=(3.0,5.0), params=params)
            except Timeout as e:
                time.sleep(5)
                continue
            else:
                break
        else:
            res = None

        return res

    def _get_soup(self, res):
        soup = bs4(res.content, "html.parser")

        return soup

    def _get_hrefs(self, soup, startswith="/wiki/"):
        a_list = soup.find_all("a")
        hrefs = [ a.get("href") for a in a_list if a.get("href") and a.get("href").startswith(startswith) ]

        return hrefs

    def _get_site(self, url: URL):
        res = self._get_res(url)
        soup = self._get_soup(res)
        hrefs = self._get_hrefs(soup)
        hist = collections.Counter(hrefs).most_common()
        
        hrefs = [ Href(
            source = url,
            target = URL(url.domain+href[0]),
            weight = href[1],
            firstPass = "yet",
            lastPass = "yet",
            passNumber= 0,
            isActive = True,
            score = 0.0
        ) for href in hist ]

        site = Site(
            url = url
            firstVisit = res.headers["Date"],
            lastVisit = res.headers["Date"],
            visitNumber = 1,
            isActive = True,
            score = 0.0,
            contents = hashlib.sha1(res.text.encode("utf-8")).hexdigest()
            hrefs = hrefs
        )

        return site

    def _crawling(
            self,
            interval = 5,
            max_length = 100
        ):
        """
        1 unit of process for a crawling
        """

        # check the length of 1 crawling
        def cont1():
            return len(self.footprint) < max_length

        # check if return back to the start position
        def cont2():
            if len(self.footprint) == 1:
                return True

            return self.footprint[0] != self.footprint[-1]

        self._init_footprint()
        print(f"start a touring!")

        loop = 0
        while cont1() and cont2():
            print(f"l{loop}:now i\'m in {self._parent.data.url}")
            try: 
                self._update_index(interval=interval)
            except ValueError as e:
                raise e

            try:
                self._update_footprint()
            except Exception as e:
                raise e

            loop += 1
        else:
            index = [ dataclasses.asdict(data) for data in self.index ]
            footprint = [ dataclasses.asdict(data) for data in self.footprint ]

            self._dump_json(index, self.index_path)
            self._dump_json(footprint, f"{self._dirname}{self._fp_timestamp}.cycle.json")

            print(f"\nfinished a touring properly!")

    def touring(
            self,
            interval = 5,
            max_length = 100,
            lifetime = timedelta(hours=1)
        ):
        till = datetime.now() + lifetime

        while datetime.now() < till:
            start = datetime.now()
            try:
                self._crawling(interval=interval, max_length=max_length)
            except ValueError as e:
                raise e

            end = datetime.now()
            t = end - start
            print(f"touring time: {t}\n")


