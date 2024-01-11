import pytest

# modules to test
from src.crawler import HrefScreen, Index, Crawler

@pytest.mark.parametrize(('url', 'expected'), [
    ("https://docs.python.org/ja/3/library/urllib.html", False),
    ("https://docs.python.org/ja/3/library/internet.html", False),
    ('https://tech-unlimited.com/urlencode.html', False),
    ("https://docs.python.org/ja/3/library/urllib.parse.html#urllib.parse.ParseResult", False),
    ("https://qiita.com/motoki1990/items/8275dbe02d5fd5fa6d2d", False),
    ("https://qiita.com/ttyszk/items/01934dc42cbd4f6665d2", "https://qiita.com/ttyszk/items/01934dc42cbd4f6665d2"),
    ("/ttyszk/items/01934dc42cbd4f6665d2", "https://qiita.com/ttyszk/items/01934dc42cbd4f6665d2"),
    ('/advent-calendar', False),
    ('/login?callback_action=login_or_signup&redirect_to=%2Fttyszk%2Fitems%2F01934dc42cbd4f6665d2&realm=qiita', False),
    ("math.jp", False),
])
def test_HrefScreen(url, expected):
    p_cnd1 = urlparts("", "", r"^/ttyszk/.*", "", "", "")
    p_cnd2 = urlparts("https", "qiita.com", r"^/ttyszk/.*", "", "", "")
    p_fmt = urlparts("https", "qiita.com", None, None, None, None)

    pattern = HrefScreen([p_cnd1, p_cnd2], p_fmt)
    assert pattern(url) == expected
    pass