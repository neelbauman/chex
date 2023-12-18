"""
Recconaissance Unit
"""

import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup as bs4

import os, sys
import json, re, time, random, collections, dataclasses
from datetime import timedelta, datetime


class Crawler(Handler):
    """
    Survey Unit
    """
    base_dir = "tmp/"

    def __init__(self, domain:str = "", *args, **kwargs):
        self.domain = domain
        self.dir_name = base_dir + self._hash_name(self._url_encode(domain), extension="/")
        self.file_name = "index.json"
        self.index_path = self.dir_name + self.file_name
        self._args = args
        self._kwargs = kwargs
        self._init_index()
        #self._init_footprint()
    
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

    @property
    def dir_name(self):
        return self._dir_name
    @dir_name.setter
    def dir_name(self, value):
        self._dir_name = value

    @property
    def file_name(self):
        return self._file_name
    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def index_path(self):
        return self._index_path
    @index_path.setter
    def index_path(self, value):
        self._index_path = value

    def _init_index(self) -> None:
        """
        load or make domain/index.json
        """
        try:
            index = self._load_json(self.index_path)
            self.index = [ SiteData(
                url = data["url"],
                first = data["first"],
                last = data["last"],
                active = data["active"],
                n_refed = data["n_refed"],
                n_visited = data["n_visited"],
                score = data["score"],
                hrefs = [ Href(**href) for href in data["hrefs"] ],
            )
            for data in index ]
            print(f"success in loading {self.index_path} and _init_index()\n")
        except Exception as e:
            try:
                os.makedirs(self.dir_name)
            except Exception as e:
                pass
            finally:
                with open(self.index_path, "w") as f:
                    f.write("")
                self.index = []

    def _init_footprint(self) -> None:
        """
        """
        n = len(self.index)
        if n == 0:
            """
            self.indexが空ならlpを取得して最初の要素にする
            """
            lp = self._get_lp()
            self.index.append(lp.data)
            self._parent= lp
            self._data = None
        else:
            """
            self.indexが空でないなら
            """
            fail_list = []
            while True:
                r = random.randrange(n)
                if r in fail_list:
                    if len(fail_list) >= n:
                        raise Exception("All url is not valid")
                    continue

                p_data = self.index[r]

                try:
                    p_contents = self._get_res(p_data.url).text
                except Timeout as e:
                    fail_list.append(r)
                    continue
                else:
                    break

            self._parent = Site(p_data, p_contents)
            self._data = None

        self.footprint = [self._parent.data]
        self._fp_timestamp = datetime.now().strftime("%Y%m%d:%H:%M:%S")

    def _select_target_href(self, algorithm:int = 0):
        hrefs = self._parent.data.hrefs
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

    def _update_footprint(self) -> None:
        self.footprint.append(self._target.data)
        self._parent = self._target

    def _get_lp(self) -> Site:
        """
        get LP which is a page that is redirected from server root like https://math.jp
        """
        loop = 0
        while loop < 10:
            try:
                res = self._get_res(self.domain)
                break
            except Timeout as e:
                print(e)
        else:
            raise Exception("")

        lp_data, lp_contents = self._get_data_and_contents(res)
        lp = Site(lp_data, lp_contents)

        self._lp_url = lp.data.url

        return lp

    def _load_json(self, file_path):
        try:
            with open(file_path, "r") as f:
                s = f.read()
            data = json.loads(s)
        except Exception as e:
            data = []

        return data

    def _dump_json(self, data, file_path):
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
        except:
            raise Exception(f"some error with dump {data}")

        return True

    def _get_res(self, url:str, **kwargs) -> requests.models.Response:
        """
        if get returns Timeout, try 10 times anothor.
        if those failed, then raise Timeout for the first time.
        """
        url = self._url_encode(url)
        params = kwargs if kwargs else None

        loop = 0
        while True:
            try:
                res = requests.get(url, timeout=(3.0,5.0), params=params)
            except Timeout as e:
                loop += 1
                if loop < 10:
                    time.sleep(10)
                    continue
                else:
                    raise e
            else:
                break

        return res

    def _get_soup(self, res):
        soup = bs4(res.content, "html.parser")

        return soup

    def _get_hrefs(self, soup, startswith="/wiki/"):
        a_list = soup.find_all("a")
        hrefs = [ a.get("href") for a in a_list if a.get("href") and a.get("href").startswith(startswith) ]

        return hrefs

    def _get_data_and_contents(self, res) -> (SiteData, Contents):
        soup = self._get_soup(res)
        hrefs = self._get_hrefs(soup)

        hist = collections.Counter(hrefs).most_common()
        
        hrefs = [ Href(
            url = self._url_encode(self.domain+href[0]),
            first = "yet",
            last = "yet",
            active = True,
            n_ref = href[1],
            n_passed = 0,
            score = 0
        ) for href in hist ]

        data = SiteData(
            url = self._url_encode(res.url),
            first = res.headers["Date"],
            last = res.headers["Date"],
            active = True,
            n_refed = 0,
            n_visited = 1,
            score = 0,
            hrefs = hrefs
        )

        contents = Contents(html=res.text)

        return data, contents

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
            self._dump_json(footprint, f"{self._dir_name}{self._fp_timestamp}.cycle.json")

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


