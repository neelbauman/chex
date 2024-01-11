import pytest
from urllib.parse import urlparse, urlunparse, quote, unquote

# modules to test
from src.datatype.adt import stack, queue
from src.datatype.collections import urlparts, dom2dir, dir2dom
from src.datatype.web import URL, Site, Href


def test_urlparts():
    up = urlparts(
        "https",
        "math.jp",
        "/path/to/somewhere",
        "param",
        "query",
        "fragment",
    )

    assert up.scheme == "https"
    assert up.netloc == "math.jp"
    assert up.path == "/path/to/somewhere"
    assert up.param == "param"
    assert up.query == "query"
    assert up.fragment == "fragment"

    url = urlunparse(up)
    
    assert url == "https://math.jp/path/to/somewhere;param?query#fragment"

def test_dom2dir():
    dd = dom2dir("https://quiita.com", "tmp/fajgoaga30irqj/")

    assert dd.domain == "https://quiita.com"
    assert dd.dirname == "tmp/fajgoaga30irqj/"
    assert dd._asdict()["https://quiita.com"] == "tmp/fajgoaga30irqj/"

def test_dir2dom():
    dd = dir2dom("tmp/fajgoaga30irqj/", "https://quiita.com",)

    assert dd.domain == "https://quiita.com"
    assert dd.dirname == "tmp/fajgoaga30irqj/"
    assert dd._asdict()["tmp/fajgoaga30irqj/"] == "https://quiita.com"


