from collections import namedtuple

urlparts = namedtuple("urlparts", "scheme netloc path param query fragment")

dom2dir = namedtuple("domain2dirname", "domain dirname")
dir2dom = namedtuple("dirname2domain", "dirname domain")

# node-link json format for graph
nodetuple = namedtuple("nodetuple", "id attr")
edgetuple = namedtuple("edgetuple", "source target attr")
