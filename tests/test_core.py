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

domain = "https://math.jp"
lp = "/wiki/メインページ"
target = "/wiki/%E6%B8%AC%E5%BA%A6%E3%81%A8%E7%A9%8D%E5%88%861%EF%BC%9A%E6%B8%AC%E5%BA%A6%E8%AB%96%E3%81%AE%E5%9F%BA%E7%A4%8E%E7%94%A8%E8%AA%9E"


class TestCrawler(object):

    def url_encode(self, url:str):
        encoded = urllib.parse.quote(url, safe=":/%")

        return encoded

    def hash_name(self, url):
        url = self.url_encode(url)
        name = hashlib.sha1(url.encode("utf-8")).hexdigest() + ".json"
        return name

    def test_url_encode(self):
        assert target == self.url_encode(target)

    def test_init(self):
        crawler = Crawler(domain)
        assert crawler._domain == domain

    def test_get_lp(self):
        crawler = Crawler(domain)
        lp_url = crawler._get_lp()
        assert lp_url == self.url_encode(domain+lp)

    def test_get_res(self):
        crawler = Crawler(domain)
        res = crawler.get_res(target)
        assert res.status_code == 200

    def test_load(self):
        crawler = Crawler(domain)
        url = domain + target
        name = self.hash_name(url)
        
        data = crawler.load(f"../tmp/{name}")
        print(f"\n\ntmp/{name}\n\n")
        assert data

    def test_make_soup(self):
        crawler = Crawler(domain)
        res = crawler.get_res(target)
        data = crawler.get_json(res)
        assert data["hrefs"]

