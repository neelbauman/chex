"""
Recconaissance Unit
"""

import networkx as nx
import requests
from requests.exceptions import Timeout
from requests.models import Response
from bs4 import BeautifulSoup as bs4

import os
import json
import re
import time
import random
import collections
import urllib
import hashlib
from datetime import timedelta, datetime

from dataclass import URL, Href, Contents, Site
from datatype.darray import queue, stack


Attr = collections.namedtuple("Attr", "key value")
Edge = collections.namedtuple("Edge", "source target attr")



class Index():
    def __init__(
        self,
        filepath: str = "",
    ):
        self.filepath = filepath

        try:
            self.G = self.readEdgelist(filepath)
        except:
            self.G = nx.DiGraph()
            self.writeEdgelist(filepath)

    @property
    def filepath(self) -> str:
        return self._filepath
    @filepath.setter
    def filepath(self, value: str):
        self._filepath = os.path.normpath(value)

    @property
    def dirname(self) -> str:
        try:
            dirname = os.path.dirname(self.filepath)
        except Exception as e:
            raise ValueError(f"Invalid Filepath: {self.filepath}")
        else:
            return dirname

    @property
    def filename(self) -> str:
        try:
            filename = os.path.basename(self.filepath)
        except Exception as e:
            raise ValueError(f"Invalid Filepath: {self.filepath}")
        else:
            return filename
        
    def readEdgelist(self, filepath: str = ""):
        path = filepath if filepath else self.filepath
        _, ext = os.path.splitext(path)

        if ext == ".csv":
            delimiter = ","
        elif ext == ".tsv":
            delimiter = "\t"
        else:
            delimiter = None

        self.G = nx.read_edgelist(
            path = path,
            comments = '#',
            delimiter = delimiter,
            create_using = nx.DiGraph,
            data = (
                Attr("weight", int),
                Attr("score", float),
                Attr("isActive", bool),
                Attr("timestamp", datetime.datetime),
            ),
            encoding = 'utf-8',
        )

    def readWeightedEdgelist(self):

        G = nx.read_weighted_edgelist(
            path = path,
            comments = '#',
            delimiter = delimiter,
            create_using = nx.DiGraph,
            nodetype = None,
            encoding='utf-8',
        )

    def writeEdgelist(self, filepath: str = ""):
        path = filepath if filepath else self.filepath
        _, ext = os.path.splitext(path)

        if ext == ".csv":
            delimiter = ","
        elif ext == ".tsv":
            delimiter = "\t"
        else:
            delimiter = " "

        try:
            os.makedirs(self.dirname)
        except Exception as e:
            pass
        finally:
            nx.write_edgelist(
                G = self.G,
                path = path,
                comments = '#',
                delimiter = delimiter,
                data = True,
                encoding = 'utf-8',
            )


    def readJson(self, filepath: str = ""):
        path = filepath if filepath else self.filepath
        try:
            with open(path, "r") as f:
                s = f.read()
                data = json.loads(s)
        except Exception as e:
            raise e 
        else:
            return data

    def writeJson(self, filepath: str = ""):
        path = filepath if filepath else self.filepath
        try:
            os.makedirs(self.dirname)
        except Exception as e:
            pass
        finally:
            with open(path, "w") as f:
                json.dump(self.json, f, indent=4)


class Controller():
    def __init__(self, *args, **kwargs):
        self.footprint = []
        self.waitlist = []

    def update_waitlist(self, hrefs: [Href]) -> None:
        self.waitlist = [*self.waitlist, *hrefs]

    def get_next(self) -> Href:
        return self.waitlist.pop()



class Crawler():
    """
    Survey Unit
    """
    base_dir = "tmp"

    def __init__(
        self,
        domain: str = "",
        url: str = "",
        filename: str = "index.csv",
    ):
        if url:
            self.domain = URL(url).domain
        elif domain:
            self.domain = URL(domain)
        else:
            raise NotImplemented

        self._init_index(filename)
        self._init_controller(url)
    
    @property
    def domain(self):
        return self._domain
    @domain.setter
    def domain(self, value):
        self._domain = value

    def _init_index(self, filename):
        indexpath = os.path.join(self.base_dir, self.domain.hashed, filename)
        self.index = Index(indexpath)

    def _init_controller(self, url):
        self.controller = Controller()

        if url:
            res = self.get_res(URL(url))
        else:
            res = self.get_res(self.domain)

        hrefs = self._get_hrefs(res)

        self.controller.update_waitlist(hrefs)

    def get_res(self, url: URL, n_try: int = 10, **kwargs) -> Response | None:
        """
        if requests.get raises Timeout Exception, try 10 times anothor.
        if those are failed, then return None.
        """
        url = url.encoded
        params = kwargs if kwargs else None

        for loop in range(n_try):
            try:
                res = requests.get(url, timeout=(3.0,5.0), params=params)
            except Timeout as e:
                time.sleep(5)
                loop += 1
                continue
            else:
                break
        else:
            res = None

        return res

    def _get_soup(self, res, parser: str = "html.parser"):
        soup = bs4(res.content, parser)
        return soup

    def _get_hrefs(self, res, startswith="/"):
        soup = self._get_soup(res)
        a_list = soup.find_all("a")
        targets = [
            a.get("href") for a in a_list
            if a.get("href") and a.get("href").startswith(startswith)
        ]
        
        hrefs = [ Href(
            source = URL(res.url),
            target = URL(target),
            weight = 1,
            score = 0.0,
            isActive = False,
        ) for target in targets ]

        return hrefs

    def _get_next(self):
        return self.controller.get_next()

    def update(self):
        """
        """
        href = self._get_next()
        res = self.get_res(href.target)

        if res is None:
            href.deactivate()
            status = -1
        else:
            href.activate()
            status = 1

        # targetが未到達の場合のみ、
        # targetから伸びるhrefsをwaitlistに追加
        if not href.target in self.index.G.nodes:
            new_hrefs = self._get_hrefs(res)
            self.controller.update_waitlist(new_hrefs)

        self.index.G.add_edge(href.source, href.target, href.attr_dict)

        return href, status

    def crawl(
        self,
        interval = 5,
        max_length = 100,
    ):
        """
        ## waitlistが空になるまでself.update()し続ける
        """
        print(f"Start Crawling!")

        loop = 0
        while not self.controller.waitlist.isEmpty:
            DONE = self.update()
            print(f"l{loop}: from {DONE.source} to {DONE.target}")
            loop += 1
        else:
            index = [ dataclasses.asdict(data) for data in self.index ]
            footprint = [ dataclasses.asdict(data) for data in self.footprint ]

            self._dump_json(index, self.index_path)
            self._dump_json(footprint, f"{self._dirname}{self._fp_timestamp}.cycle.json")

            print(f"\nfinished a touring properly!")

