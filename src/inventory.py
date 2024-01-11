import os
import json
from datetime import datetime 
from random import choice
from itertools import chain, count

# networkxへの依存はここに局所化する。
import networkx as nx

from src.datatype.collections import nodetuple, edgetuple
from src.datatype.web import Site, Href

# graph_formatとしてnode_link形式のJSONを取り扱うために、
# - nx.Graph <-> python.dictの変換を行う二つの関数node_link_data(G), node_link_graph(data)
# - python.dict <-> JSON の変換を行うためのEncoderとobject_hook for Decoder
# を用意する。

_attrs = {
    "source": "source",
    "target": "target",
    "name": "id",
    "key": "key",
    "link": "links",
    "node": "nodes",
}

def _to_tuple(x):
    """Converts lists to tuples, including nested lists.

    All other non-list inputs are passed through unmodified. This function is
    intended to be used to convert potentially nested lists from json files
    into valid nodes.

    Examples
    --------
    >>> _to_tuple([1, 2, [3, 4]])
    (1, 2, (3, 4))
    """
    if not isinstance(x, (tuple, list)):
        return x
    return tuple(map(_to_tuple, x))

# @nx._dispatch(graphs=None)
def node_link_graph(
    data,
    directed=False,
    multigraph=True,
    *,
    source="source",
    target="target",
    name="id",
    key="key",
    link="links",
):
    """Returns graph from node-link data format.
    Useful for de-serialization from JSON.

    Parameters
    ----------
    data : dict
        node-link formatted graph data

    directed : bool
        If True, and direction not specified in data, return a directed graph.

    multigraph : bool
        If True, and multigraph not specified in data, return a multigraph.

    source : string
        A string that provides the 'source' attribute name for storing NetworkX-internal graph data.
    target : string
        A string that provides the 'target' attribute name for storing NetworkX-internal graph data.
    name : string
        A string that provides the 'name' attribute name for storing NetworkX-internal graph data.
    key : string
        A string that provides the 'key' attribute name for storing NetworkX-internal graph data.
    link : string
        A string that provides the 'link' attribute name for storing NetworkX-internal graph data.

    Returns
    -------
    G : NetworkX graph
        A NetworkX graph object

    Examples
    --------

    Create data in node-link format by converting a graph.

    >>> G = nx.Graph([('A', 'B')])
    >>> data = nx.node_link_data(G)
    >>> data
    {'directed': False, 'multigraph': False, 'graph': {}, 'nodes': [{'id': 'A'}, {'id': 'B'}], 'links': [{'source': 'A', 'target': 'B'}]}

    Revert data in node-link format to a graph.

    >>> H = nx.node_link_graph(data)
    >>> print(H.edges)
    [('A', 'B')]

    To serialize and deserialize a graph with JSON,

    >>> import json
    >>> d = json.dumps(node_link_data(G))
    >>> H = node_link_graph(json.loads(d))
    >>> print(G.edges, H.edges)
    [('A', 'B')] [('A', 'B')]


    Notes
    -----
    Attribute 'key' is only used for multigraphs.

    To use `node_link_data` in conjunction with `node_link_graph`,
    the keyword names for the attributes must match.

    See Also
    --------
    node_link_data, adjacency_data, tree_data
    """
    multigraph = data.get("multigraph", multigraph)
    directed = data.get("directed", directed)
    if multigraph:
        graph = nx.MultiGraph()
    else:
        graph = nx.Graph()
    if directed:
        graph = graph.to_directed()

    # Allow 'key' to be omitted from attrs if the graph is not a multigraph.
    key = None if not multigraph else key
    graph.graph = data.get("graph", {})
    c = count()
    for d in data["nodes"]:
        node = _to_tuple(d.get(name, next(c)))
        nodedata = {str(k): v for k, v in d.items() if k != name}
        graph.add_node(node, **nodedata)
    for d in data[link]:
        src = tuple(d[source]) if isinstance(d[source], list) else d[source]
        tgt = tuple(d[target]) if isinstance(d[target], list) else d[target]
        if not multigraph:
            edgedata = {str(k): v for k, v in d.items() if k != source and k != target}
            graph.add_edge(src, tgt, **edgedata)
        else:
            ky = d.get(key, None)
            edgedata = {
                str(k): v
                for k, v in d.items()
                if k != source and k != target and k != key
            }
            graph.add_edge(src, tgt, ky, **edgedata)
    return graph

def node_link_data(
    G: nx.Graph,
    *,
    source: str = "source",
    target: str = "target",
    name: str = "id",
    key: str = "key",
    link: str = "links",
):
    """Returns data in node-link format that is suitable for JSON serialization

    Parameters
    ----------
    G : NetworkX graph
    source : string
        A string that provides the 'source' attribute name for storing NetworkX-internal graph data.
    target : string
        A string that provides the 'target' attribute name for storing NetworkX-internal graph data.
    name : string
        A string that provides the 'name' attribute name for storing NetworkX-internal graph data.
    key : string
        A string that provides the 'key' attribute name for storing NetworkX-internal graph data.
    link : string
        A string that provides the 'link' attribute name for storing NetworkX-internal graph data.

    Returns
    -------
    data : dict
       A dictionary with node-link formatted data.

    Raises
    ------
    NetworkXError
        If the values of 'source', 'target' and 'key' are not unique.

    Examples
    --------
    >>> G = nx.Graph([("A", "B")])
    >>> data1 = nx.node_link_data(G)
    >>> data1
    {'directed': False, 'multigraph': False, 'graph': {}, 'nodes': [{'id': 'A'}, {'id': 'B'}], 'links': [{'source': 'A', 'target': 'B'}]}

    To serialize with JSON

    >>> import json
    >>> s1 = json.dumps(data1)
    >>> s1
    '{"directed": false, "multigraph": false, "graph": {}, "nodes": [{"id": "A"}, {"id": "B"}], "links": [{"source": "A", "target": "B"}]}'

    A graph can also be serialized by passing `node_link_data` as an encoder function. The two methods are equivalent.

    >>> s1 = json.dumps(G, default=nx.node_link_data)
    >>> s1
    '{"directed": false, "multigraph": false, "graph": {}, "nodes": [{"id": "A"}, {"id": "B"}], "links": [{"source": "A", "target": "B"}]}'

    The attribute names for storing NetworkX-internal graph data can
    be specified as keyword options.

    >>> H = nx.gn_graph(2)
    >>> data2 = nx.node_link_data(H, link="edges", source="from", target="to")
    >>> data2
    {'directed': True, 'multigraph': False, 'graph': {}, 'nodes': [{'id': 0}, {'id': 1}], 'edges': [{'from': 1, 'to': 0}]}

    Notes
    -----
    Graph, node, and link attributes are stored in this format.  Note that
    attribute keys will be converted to strings in order to comply with JSON.

    Attribute 'key' is only used for multigraphs.

    To use `node_link_data` in conjunction with `node_link_graph`,
    the keyword names for the attributes must match.


    See Also
    --------
    node_link_graph, adjacency_data, tree_data
    """
    directedgraph = G.is_directed()
    multigraph = G.is_multigraph()

    # Allow 'key' to be omitted from attrs if the graph is not a multigraph.
    key = None if not multigraph else key
    if len({source, target, key}) < 3:
        raise nx.NetworkXError("Attribute names are not unique.")
    
    # make nodes
    data = {
        "directed": directedgraph,
        "multigraph": multigraph,
        "graph": G.graph,
        "nodes": [{**G.nodes[n], name: n} for n in G],
    }
    # make links
    if multigraph:
        data[link] = [
            {**d, source: u, target: v, key: k}
            for u, v, k, d in G.edges(keys=True, data=True)
        ]
    else:
        data[link] = [ {**d, source: u, target: v} for u, v, d in G.edges(data=True) ]
    return data


class CustomJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder to serialize node_link_data made from Graph with node_link_data()
    """
    strftime_fmt: str = "%Y-%m-%dT%H:%M:%S.%f+09:00"

    def default(self, obj):
        if type(obj) is datetime:
            return {"fmt": "ISO8601", "datetime": obj.strftime(self.strftime_fmt)}
        else:
            return super().default(obj)

def as_datetime(adict):
    """
    object_hook used by JSON Decoder to decode json node_link_data.
    """
    strftime_fmt: str = "%Y-%m-%dT%H:%M:%S.%f+09:00"
    if "fmt" in adict:
        return datetime.strptime(adict["datetime"], strftime_fmt)
    return adict


class Inventory():
    """
    - いろんな形式のグラフフォーマットをロードできること
    - それらをすべて一貫した形式、つまり、Siteオブジェクトをノードにしたグラフ
    Siteオブジェクトは、グラフに加えられるときに正しくkeyとattrに分離されなければならない。
    これにより、nx.Graphのデータ構造やその上で駆動するアルゴリズムの恩恵を受けられる。
    逆に、グラフからkeyで読み出される時には、正しくSiteオブジェクトとして取り出されなければならない。
    
    """
    filename_fmt = "%Y%m%dT%H%M%S%f"

    @property
    def filepath(self) -> str:
        return os.path.join(self.dirname, self.basename)
    @filepath.setter
    def filepath(self, value: str|None):
        filepath = value or ""
        self._dirname, _ = os.path.split(filepath)
        self._filename, self._ext = os.path.splitext(_)

    @property
    def dirname(self):
        return self._dirname
    @dirname.setter
    def dirname(self, value: str):
        self._dirname = value

    @property
    def basename(self):
        return self.filename + self.ext
    @basename.setter
    def basename(self, value: str):
        self._filename, self._ext = os.path.splitext(value)

    @property
    def filename(self):
        return self._filename
    @filename.setter
    def filename(self, value: str):
        self._filename = value

    @property
    def ext(self):
        return self._ext
    @ext.setter
    def ext(self, value: str):
        self._ext = value

    @property
    def nodes(self):
        return self.G.nodes

    @property
    def edges(self):
        return self.G.edges

    @property
    def isEmpty(self):
        return nx.is_empty(self.G)

    def __getitem__(self, key):
        return self.get_node(key)

    def __contains__(self, key):
        return key in self.G

    def __repr__(self):
        return f"<Inventory file:{self.filepath} at 0x{id(self):x}>"

    def __init__(
        self,
        filepath: str|None = None,
        seed: str|None  = None
    ):
        # initialize self.filepath
        self.timestamp = datetime.now()
        self.filepath = filepath
        if not self.filename:
            self.filename = self.timestamp.strftime(self.filename_fmt)

        # initialize self.G
        try:
            self.load(self.filepath)
        except ValueError as e:
            self.G = nx.DiGraph(
                seed = seed,
                timestamp = self.timestamp.strftime(self.filename_fmt),
            )
            print(f"Success in Init {self.filepath}.")
        else:
            print(f"Success in Loading {self.filepath}.")

        # initialize self.seed
        self.set_seed(seed)

    def set_seed(self, seed: str|None = None):
        if seed:
            self.seed = seed
            self.G.graph["seed"] = seed
        else:
            try:
                self.seed = self.G.graph["seed"]
            except KeyError as ke:
                try:
                    self.seed = choice(self.G.nodes)
                except IndexError as e:
                    raise ValueError(f"NoneSeedError. To Init New Graph, Give seed:given \"{seed}\"")
                else:
                    self.G.graph["seed"] = self.seed

    def load(self, filepath: str|None = None, graph_format: str|None = None):
        # TODO データのファイル形式とグラフ形式の組み合わせ問題の解決
        filepath = filepath or self.filepath
        try:
            loader_dict = self._loader_dict
        except AttributeError as e:
            loader_dict = {
                "edgelist": self.loadEdgelist,
                "json": self.loadJSON,
            }
            self._loader_dict = loader_dict

        try:
            loader_dict[graph_format](filepath)
        except (TypeError, KeyError):
            for key, loader in loader_dict.items():
                try:
                    loader(filepath)
                    break
                except FileNotFoundError as e:
                    continue
            else:
                raise ValueError(f"Invalid File Format: \"{graph_format}\", and Could Not Open \"{filepath}\"")

    def write(self, filepath: str|None = None, graph_format: str|None = None):
        filepath = filepath or self.filepath
        try:
            writer_dict = self._writer_dict
        except AttributeError as e:
            writer_dict = {
                "edgelist": self.writeEdgelist,
                "json": self.writeJSON,
            }
            self._writer_dict = writer_dict
        
        try:
            writer_dict[graph_format](filepath)
        except (KeyError, TypeError) as e:
            graph_format = "json"
            writer_dict[graph_format](filepath)
            print(f"Dumped to {filepath} as {graph_format}")
        else:
            print(f"Success in Writing {filepath} as {graph_format}")


    def get_node(self, key: str) -> Site:
        """
        グラフのnodeからSiteオブジェクトを作る
        """
        try:
            attr: dict = self.G.nodes[key]
        except KeyError as e:
            raise e
        try:
            return Site(key, **attr)
        except TypeError as e:
            prcd_attr = {
                attr_key: attr_value
                for attr_key, attr_value in attr.items()
                if attr_key in Site.__annotations__
            }
            return Site(key, **prcd_attr)

    def set_node(self, site: Site, safe: bool = True):
        """
        Siteオブジェクトからグラフのnodeを作る、または更新する
        """
        node: nodetuple = site.asNode()
        if safe:
        # すでに存在しているノードに関しては、"first"と"url"は更新しない。
            try:
                attr:dict = self.G.nodes[node.id]
            except KeyError as e:
                self.G.add_node(node.id, **node.attr)
            else:
                ignore_key = ["url", "first", "last", "timestamp"]
                attr["last"] = attr.pop("timestamp")
                attr["timestamp"] = node.attr["timestamp"]
                for key, value in node.attr.items():
                    if key in ignore_key:
                        pass
                    else:
                        attr[key] = value
        else:
            self.G.add_node(node.id, **node.attr)

    def get_edge(self, source: str, target: str) -> Href:
        attr: dict = self.G.edges[source,target]
        source = self.get_node(source)
        target = self.get_node(target)
        try:
            return Href(source, target, **attr)
        except TypeError as e:
            prcd_attr = {
                attr_key: attr_value
                for attr_key, attr_value in attr.items()
                if attr_key in Href.__annotations__
            }
            return Href(source, target, **prcd_attr)

    def set_edge(
        self,
        href: Href,
        safe: bool = True,
        update_source: bool = True,
        update_target: bool = True,
    ):
        """
        Hrefオブジェクトからグラフのedgeをつくる、または更新する
        """
        if update_source:
            self.set_node(href.source, safe)
        if update_target:
            self.set_node(href.target, safe)
        edge: edgetuple = href.asEdge()
        self.G.add_edge(edge.source, edge.target, **edge.attr)
        
    def loadEdgelist(self, filepath: str, delimiter: str|None = None):
        _, ext = os.path.splitext(filepath)
        if ext != "edgelist":
            raise FileNotFoundError

        if delimiter:
            delimiter = delimiter
        else:
            if ext == ".csv":
                delimiter = ","
            elif ext == ".tsv":
                delimiter = "\t"
            else:
                delimiter = " "

        self.G = nx.read_edgelist(
            path = filepath,
            comments = '#',
            delimiter = delimiter,
            create_using = nx.DiGraph,
            data = (
                ("weight", int),
                ("score", float),
                ("isActive", bool),
                ("timestamp", str),
            ),
            encoding = 'utf-8',
        )

        self.filepath = filepath
        ts = os.path.getctime(filepath)
        self.timestamp = datetime.fromtimestamp(ts)
        self.isLoadSuccessed = True


    def writeEdgelist(self, filepath: str|None = None, delimiter: str|None = None):
        filepath = filepath or self.filepath
        if delimiter:
            delimiter = delimiter
        else:
            _, ext = os.path.splitext(filepath)
            if ext == ".csv":
                delimiter = ","
            elif ext == ".tsv":
                delimiter = "\t"
            else:
                delimiter = " "

        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as e:
            pass
        finally:
            nx.write_edgelist(
                G = self.G,
                path = filepath,
                comments = '#',
                delimiter = delimiter,
                data = ["weight", "score", "isActive", "timestamp"],
                encoding = 'utf-8',
            )

    def loadJSON(self, filepath: str):
        _, ext = os.path.splitext(filepath)
        if ext != ".json":
            raise FileNotFoundError

        with open(filepath, "r") as f:
            data = json.load(f, object_hook=as_datetime)

        #print(data)
        self.G = node_link_graph(
            data = data,
            directed = True,
            multigraph = True,
        )

        self.filepath = filepath
        ts = os.path.getctime(filepath)
        self.timestamp = datetime.fromtimestamp(ts)
        self.isLoadSuccessed = True

    def writeJSON(self, filepath: str):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as e:
            pass
        finally:
            data = self.asJSON()
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4, cls=CustomJSONEncoder)

    def asJSON(self):
        return node_link_data(G=self.G)

