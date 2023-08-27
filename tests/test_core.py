"""
* 実践TDD with pytest

** テストのパラメタライズ
逐次実行でエラーが起きたらテスト終了ではなく、
定義された範囲でパラメータを全走査して結果をまとめて返す。

** フィクスチャ
テスト環境の動的な整備と後処理

*** 基本的な前処理と後処理
*** テンポラリの作成
*** fixtureのスコープの変更
*** conftest.py
*** 標準出力のキャプチャ

** モック（発展）
仕様と実装の整合性、関数、クラス、モジュール間の依存関係のテスト
pytest-mockというプラグインが必要

* 単体テストという考え方

"""
import pytest
from src.crawler import Crawler

import urllib, hashlib, json
from typing import Dict

@pytest.fixture
def domain() -> str:
    yield "https://math.jp"

@pytest.fixture
def target() -> str:
    yield "/wiki/メインページ"


class TestCrawler(object):
    domain = "https://math.jp"
    lp = "/wiki/メインページ"
    target = "/wiki/%E6%B8%AC%E5%BA%A6%E3%81%A8%E7%A9%8D%E5%88%861%EF%BC%9A%E6%B8%AC%E5%BA%A6%E8%AB%96%E3%81%AE%E5%9F%BA%E7%A4%8E%E7%94%A8%E8%AA%9E"

    def url_encode(self, url):
        url = urllib.parse.quote(url, safe=":/")
        return url

    def hash_name(self, url):
        name = hashlib.sha1(url.encode("utf-8")).hexdigest() + ".json"
        return name

    def test_init(self):
        crawler = Crawler(TestCrawler.domain)
        assert crawler._domain == TestCrawler.domain

    def test_get_lp(self):
        crawler = Crawler(TestCrawler.domain)
        domain = TestCrawler.domain
        lp = TestCrawler.lp
        
        lp_url = crawler._get_lp()

        assert crawler._lp_url == self.url_encode(domain+lp)

    def test_get(self):
        crawler = Crawler(TestCrawler.domain)
        res = crawler.get(TestCrawler.target)
        assert res.status_code == 200

    def test_load(self):
        crawler = Crawler(TestCrawler.domain)
        domain = TestCrawler.domain
        target = TestCrawler.target

        url = domain + target
        name = self.hash_name(url)
        
        data = crawler.load(f"tmp/{name}")

        assert data

    def test_make_soup(self):
        crawler = Crawler(TestCrawler.domain)
        domain = TestCrawler.domain
        target = TestCrawler.target

        res = crawler.get(target)
        data = crawler.make_soup(res)

        assert data["hrefs"]

