"""
requests, bs4への依存はここに局所化する
"""
import requests
from requests.exceptions import Timeout
from requests.models import Response
from bs4 import BeautifulSoup as bs4

import re
import time
from urllib.parse import ParseResult, urlparse

from src.datatype.collections import urlparts
from src.datatype.web import Site, Href

class HrefScreener:
    """
    """
    def __init__(
        self,
        format_tpl: urlparts,
        *condition_tpls: (urlparts),
    ):
        self._condition_tpls= tuple(ParseResult(*tpl) for tpl in condition_tpls)
        self._format_tpl = ParseResult(*format_tpl)

    def __eq__(self, other):
        return self is other

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
        return super().__str__()

    def __repr__(self):
        return super().__repr__()

    def __call__(self, url: str):
        result = self._convert(url)
        return result

    def check(self, url: str) -> (bool, ParseResult):
        """
        """
        parsed_tpl = urlparse(url)

        for cnd_tpl in self._condition_tpls:
            result = all( bool(re.fullmatch(cnd_part, url_part)) for cnd_part, url_part in zip(cnd_tpl, parsed_tpl) )
            if result:
                break
            else:
                continue
        else:
            return False, parsed_tpl

        return True, parsed_tpl

    def _convert(self, url: str):
        result, parsed = self.check(url)

        if result:
            for key, fmt_part in self._format_tpl._asdict().items():
                if fmt_part is not None:
                    parsed = parsed._replace(**{key: fmt_part})
                else:
                    pass
            return parsed.geturl()
        else:
            return False


class Crawler():
    """
    """

    def __init__(
        self,
        screen: HrefScreener,
    ):
        self.screen = screen

    def get_res(self, url: str, n_try: int = 10, **kwargs) -> Response | None:
        """
        if requests.get raises Timeout Exception, try 10 times anothor.
        if those are failed, then return None.
        """
        url = url
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

    def step_next(self):
        """
        """
        href: Href = self.handler.pop_next()
        res: Response = self.get_res(href.target.url)

        if res:
            href.target.activate()
            href.activate()
        else:
            href.target.deactivate()
            href.deactivate()

        soup = self._get_soup(res)
        a_list = soup.find_all("a")

        # 一回目のフィルタ
        link_list = [ a.get("href") for a in a_list if a.get("href") ]

        # 二回目のフィルタ
        url_list = [ self.screen(url) for url in link_list ]
        
        # 三回目のフィルタ
        hrefs = [ Href(
            source = href.target,
            target = Site(url),
            weight = 1,
            score = 0.0,
            isActive = False,
        ) for url in url_list if url]

        self.handler.update(href, hrefs)

        return href

    def sleep(self, interval: int):
        time.sleep(interval)
        return True

    def start(
        self,
        interval:int = 5,
        epoch:int = 1,
        epoch_length: int|None = None,
    ):
        """
        handler.waitlistが空になるまでstep_nextし続ける。
        """
        print(f"Start Crawling!")
        count = 1
        for i in range(epoch):
            print(f"===Epoch{i}===")
            loop = 0
            while ( not self.handler.isFinished ) and self.sleep(interval):
                DONE = self.step_next()
                print(f"l{loop}: QUEUE:{len(self.handler.waitlist)} {DONE}, isActive:{DONE.isActive}")
                #print(f"l{loop}: QUEUE:{len(self.handler.waitlist)}")
                count += 1
                loop += 1
                if epoch_length and loop > epoch_length-1:
                    self.handler.inventory.write()
                    print(f"===\nMax Length. Epoch{i} Finish.\n===")
                    break
            else:
                self.handler.inventory.write()
                print(f"\nFinish Crawling at Epoch{i}!")
                break
        else:
            self.handler.inventory.write()
            print(f"\nAll Epochs Finished! But QUEUE is Not Still Empty.")
        
        print("===Summary===")
        print(f"request:{count}, nodes:{len(self.handler.inventory.nodes)}, edges:{len(self.handler.inventory.edges)}")
