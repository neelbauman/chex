import pytest
from src.base import Handler
from src.crawler import Crawler, Site, SiteData, Contents

import urllib, hashlib, json
import requests


domain = "https://math.jp"
lp = "/wiki/メインページ"
target = "/wiki/%E6%B8%AC%E5%BA%A6%E3%81%A8%E7%A9%8D%E5%88%861%EF%BC%9A%E6%B8%AC%E5%BA%A6%E8%AB%96%E3%81%AE%E5%9F%BA%E7%A4%8E%E7%94%A8%E8%AA%9E"


class TestCrawler(Handler):

    def test_init(self):
        assert Crawler(domain)

    def test_get_res(self):
        crawler = Crawler(domain)
        res = crawler.get_res(domain+target)
        assert type(res) is requests.models.Response
        assert res.status_code == 200

    @pytest.mark.parametrize(
        ("file_path", "expected"), [
            ("tests/tmp/index.js", 5),
            ("tests/tmp/test.js", 0),
        ]
    )
    def test_load_index(self, file_path, expected):
        crawler = Crawler(domain)
        index = crawler._load_index(file_path)
        assert len(index) == expected

        if expected >= 1:
            assert type(crawler.index[0]) is Site


    def test_dump_index(self):
        pass

    def test_search_index(self):
        pass

    def test_make_data_and_contents(self):
        pass

    def test_select_target_href(self):
        pass

    def test_update_target(self):
        pass

    def test_update_index(self):
        pass


    def test_crawling(self):
        crawler = Crawler(domain)
        crawler.crawling
