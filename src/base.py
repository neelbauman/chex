"""
Abstruct classes
"""


class Handler(object):

    def _url_encode(self, url:str):
        encoded = urllib.parse.quote(url, safe=":/%")

        return encoded

    def _hash_name(self, s:str, extension:str):
        name = hashlib.sha1(s.encode("utf-8")).hexdigest() + extension
        
        return name
