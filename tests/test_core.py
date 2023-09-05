import pytest
from src.crawler import Crawler

import urllib, hashlib, json
from typing import Dict

domain = "https://math.jp"
lp = "/wiki/メインページ"
target = "/wiki/%E6%B8%AC%E5%BA%A6%E3%81%A8%E7%A9%8D%E5%88%861%EF%BC%9A%E6%B8%AC%E5%BA%A6%E8%AB%96%E3%81%AE%E5%9F%BA%E7%A4%8E%E7%94%A8%E8%AA%9E"


class TestCrawler(object):

    def url_encode(self, url:str):
        encoded = urllib.parse.quote(url, safe=":/%")

        return encoded

    def hash_name(self, url):
        name = hashlib.sha1(url.encode("utf-8")).hexdigest() + ".json"
        return name

    # 1.1.1
    def test_init(self):
        crawler = Crawler(domain)
        assert crawler._domain == domain

    # 1.1.2
    def test_init_index(self):
        pass

    # 1.1.3
    def test_init_footprint(self):
        pass

    # 1.1.3
    def test_init_parent(self):
        pass

    # 1.1.3
    def test_init_target(self):
        pass

    # 1.2.1
    def test_select_target_href(self):
        pass

    # 1.2.2
    def test_get_target(self):
        pass

    # 1.2.3
    def test_update_target_href(self):
        pass

    def test_get_res(self):
        crawler = Crawler(domain)
        res = crawler.get_res(domain+target)
        assert res.status_code == 200

    def test_crawling(self):
        crawler = Crawler(domain)
        crawler.crawling
