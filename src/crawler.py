"""
Recconaissance Unit
"""

from bs4 import BeautifulSoup as bs4
import requests
from requests.exceptions import Timeout

import os, sys
import json, re, datetime, time, random, collections, dataclasses

from src.base import Handler


@dataclasses.dataclass
class Contents:
    """
    Contents Unit of Site
    """
    html: str


@dataclasses.dataclass
class Href:
    """
    element of hrefs in SiteData
    """
    url: str
    first: str
    last: str
    active: bool
    n_ref: int
    n_passed: int
    score: float

    def __eq__(self, other):
        if not isinstance(other, Href):
            return NotImplemented
        return self.url == other.url

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Href):
            return NotImplemented
        return self.score < other.score

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)


@dataclasses.dataclass
class SiteData:
    """
    Data Unit of Site
    """
    url: str
    first: str
    last: str
    active: bool
    n_refed: int
    n_visited: int
    score: float
    hrefs: list[Href]

    def __eq__(self, other):
        if not isinstance(other, SiteData):
            return NotImplemented
        return self.url == other.url

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, SiteData):
            return NotImplemented
        return self.score < other.score

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)


class Site(Handler):
    """
    SiteData & Contents Unit

    """
    def __init__(self, data: SiteData, contents: Contents, *args, **kwargs) -> None:
        self._kwargs = kwargs
        self._args = args
        self.data: SiteData = data
        self.contents: Contents = contents

    # TODO Siteオブジェクト同士の演算を定義したい。
    # TODO scoreの評価
    # TODO evalContents(self, searchkeyword)
    def __str__(self):
        return self.data.url
    
    def __repr__(self):
        return self.__str__()

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        self._data = value

    @property
    def contents(self):
        return self._contents
    @contents.setter
    def contents(self, value):
        self._contetns = value


class Crawler(Handler):
    """
    Survey Unit
    """
    def __init__(self, domain:str = "", *args, **kwargs):
        base_dir = "tmp/"
        self.domain = domain
        self.dir_name = base_dir + self._hash_name(self._url_encode(domain), extension="/")
        self.file_name = "index.json"
        self.index_path = self.dir_name + self.file_name
        self._args = args
        self._kwargs = kwargs
        self._init_index()
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
            print(f"success in loading {self.index_path} and _init_index()")
            print(self.index_path)
            print(self.index)
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
            lp = self._get_lp()
            self.index.append(lp.data)
            self._parent= lp
            self._target = lp
        else:
            loop = True
            while loop:
                r = random.randrange(n)
                data = self.index[r]
                try:
                    contents = self._get_res(data.url).text
                    break
                except Timeout as e:
                    print(e)
                    continue
                except AttributeError as e:
                    print(e)
                    continue
                except Exception as e:
                    raise e

            self._parent = Site(data, contents)
            self._target = Site(data, contents)

        # TODO footprintのjsonデータの内容の強化
        self.footprint = [self._parent.data]
        self._fp_timestamp = str(datetime.datetime.now())

    def _select_target_href(self, algorithm:int = 0):
        """
        decide self._target_href from self._parent.hrefs with selected algorithm
        """
        hrefs = self._parent.data.hrefs
        n = len(hrefs)
        if n <= 1:
            raise ValueError("couldn't get next_target")

        # TODO variaous algorithm
        # completely random in self._parent.data.hrefs
        if algorithm == 0:
            r = random.randrange(n)
        # random from the n_passed == 0 ones in self._parent.data.hrefs
        elif algorithm == 1:
           yets = [ (i, href) for i, href in enumerate(hrefs) if href.n_passed == 0 ]
           if len(yets) == 0:
               r = random.randrange(n)
           else:
               q = random.randrange(len(yets))
               r = yets[q][0]
        else:
            pass

        self._target_href = hrefs[r]

    def _select_data(self):
        """
        search the target in self.index which has the same url as self._target_href.url
        """

        candidate = [ data for data in self.index if data.url == self._target_href.url ]
       
        if len(candidate) < 1:
            self._data = None
            self._i = -1
        elif len(candidate) == 1:
            i = self.index.index(candidate[0])
            self._data = self.index[i]
            self._i = i
        else:
            # TODO 一度このExceptionの発生を確認してます
            raise ValueError("there is some duplication in self.index")


    def _update_index(self, interval=5) -> None:
        """
        try to get response from links in self._parent.data.hrefs for up to 100 times
        and update self._target with that response
        """
        loop = 0
        while loop < 100:
            self._select_target_href(algorithm=0)
            self._select_data()
            try:
                time.sleep(interval)
                res = self._get_res(self._target_href.url)
            except Timeout as e:
                print(e)
                continue
            except Exception as e:
                continue
                
            if res.status_code == 200:
                break
            else:
                self._target_href.active = False
                if self._data:
                    self._data.active = False
                loop += 1
        else:
            raise ValueError(f"couldn't success in getting response from {self.domain}")

        try:
            data, contents = self._get_data_and_contents(res)
        except AttributeError as e:
            print(res.text)
            raise e

        # update self._parent.data.href[r]
        if self._target_href.last == "yet":
            self._target_href.first = res.headers["Date"]
        self._target_href.active = True
        self._target_href.n_passed += 1
        self._target_href.last = res.headers["Date"]

        # update self.index[i]
        if self._data:
            self._data.active = True
            self._data.n_visited += 1
            self._data.last = res.headers["Date"]
            data = self._data
        else:
            self._data = data
            self.index.append(data)

        self._target = Site(data, contents)

    def _update_footprint(self) -> None:
        self.footprint.append(self._target.data)
        self._parent = self._target

    def _get_lp(self) -> Site:
        """
        get LP which is a page that is redirected from server root like https://math.jp
        """
        res = self._get_res(self.domain)
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
            raise ValueError(f"some error with dump {data}")

        return True

    def _get_res(self, url:str, **kwargs) -> requests.models.Response:
        url = self._url_encode(url)
        params = kwargs if kwargs else None

        try:
            res = requests.get(url, timeout=(3.0,5.0), params=params)
        except Timeout as e:
            raise e
        except Exception as e:
            raise ValueError(f"Request Failed with some reason. Couldn't get from {url}")
        else:
            return res

    def _get_soup(self, res):
        try:
            soup = bs4(res.content, "html.parser")
        except Exception as e:
            raise e

        return soup

    def _get_hrefs(self, soup, startswith="/wiki/"):
        a_list = soup.find_all("a")

        if len(a_list) > 0:
            hrefs = [ a.get("href") for a in a_list if a.get("href").startswith(startswith) ]
        else:
            raise ValueError(f"couldn't get hrefs from soup!\n")

        return hrefs

    def _get_data_and_contents(self, res) -> (SiteData, Contents):
        try:
            soup = self._get_soup(res)
            hrefs = self._get_hrefs(soup)
        except AttributeError as e:
            print(res.headers)
            raise e
        except Exception as e:
            raise e

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

    def crawling(self, interval=5, max_length=100):
        """
        interval is the time(s) to wait to make a next request 
        """
        # TODO loopの終了条件
        # TODO footprintの初期化
        # TODO loopの再起判定と再起判定
        loop = 0
        while loop < max_length:
            print(f"l{loop}:now i\'m in {self._target.data.url}")
            self._update_index(interval=interval)
            self._update_footprint()
            loop += 1
        else:
            index = [ dataclasses.asdict(data) for data in self.index ]
            footprint = [ dataclasses.asdict(data) for data in self.footprint ]
            self._dump_json(index, self.index_path)
            self._dump_json(footprint, f"tmp/{self._fp_timestamp}.cycle.json")
            print(f"finished a walking properly!")


