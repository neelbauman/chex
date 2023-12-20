from hashlib import sha1, md5
import networkx as nx


class TreeNode():
    def __init__(
        self,
        parent = None,
        name: str | None = "",
        group: str | None = "",
        value: str | int | float | None = None,
        isDisabled: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._id = md5(hex(id(self)).encode()).hexdigest()
        self._parent = parent
        self.name = name
        self.group = group
        self.value = value
        self.isDisabled = isDisabled
        self.children = []
        
        if parent is None:
            self.index = 0
        else:
            self.attachTo(parent)
            parent.addChild(self)

    def __eq__(self, other):
        if type(other) is type(self):
            return self is other
        elif type(other) is int:
            return self.id == other
        else:
            raise ValueError(f"Not Implemented!!! Comparing {type(self)} and other: {type(other)}")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.level > other.level

    def __gt__(self, other):
        return self.level < other.level

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        parent = self.parent.id[:4] if self.parent else self.parent
        return f"<Node#{self.id:.4}..,Parent:#{parent}..,Level:{self.level}>"

    def __getitem__(self, index):
        index = int(index)
        if self.isLeaf:
            print("This is Leaf")
            return self
        else:
            return self.children[index]

    def __setitem__(self, index, item):
        index = int(index)
        if self.isLeaf:
            self.children.append(item)
        else:
            self.children[index] = item

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def isRoot(self):
        return True if self.parent is None else False

    @property
    def isLeaf(self):
        return True if len(self.children) == 0 else False

    @property
    def level(self):
        parent = self.parent
        level = 0
        while parent is not None:
            level += 1
            parent = parent.parent

        return level

    def isGroup(self, group: str):
        return self.groop == group

    def isLevel(self, lv: int):
        return self.level == lv

    def isChild(self, other):
        if type(other) is type(self):
            return self in other.children
        else:
            raise ValueError(f"Not Implemented!!! Comparing {type(self)} and other: {type(other)}")

    def isParent(self, other):
        if type(other) is type(self):
            return self is other.parent
        else:
            raise ValueError(f"Not Implemented!!! Comparing {type(self)} and other: {type(other)}")

    def isSibling(self, other):
        if type(other) is type(self):
            return self.parent is other.parent
        else:
            raise ValueError(f"Not Implemented!!! Comparing {type(self)} and other: {type(other)}")

    def addChild(self, other):
        self.children.append(other)
        other.parent = self

        return self

    def attachTo(self, other):
        other.children.append(self)
        self.parent = other

        return self

    def cutOff(self):
        self.parent.children.remove(self)
        self.parent = None

        return self

    def reduce(self):
        self.parent.children.remove(self)
        for child in self.children:
            self.parent.children.append(child)
            child.parent = self.parent

        self.parent = None
        self.children = []
        
        return self

    def view(self, label: str = "", depth: int = 0):
        tree = Tree(self)
        tree.show(label=label)
        

class Tree():
    def __init__(self, node: TreeNode | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = node
        self.G = nx.DiGraph()
        self.V = {node.id: node}

        if node:
            self.G, self.V = self._makeTree(node)

    def _makeTree(
        self,
        node: TreeNode,
        G: nx.DiGraph | None = None,
        V: dict | None = None
    ):
        G = G if G is not None else self.G
        V = V if V is not None else self.V
        
        if node.isLeaf:
            return G, V
        else:
            for c in node.children:
                G.add_node(c.id)
                G.add_edge(node.id, c.id)
                V[c.id] = c
                G, V = self._makeTree(c, G, V)
            return G, V

    def show(
        self,
        node: TreeNode | None = None,
        label: str = ""
    ):
        if node:
            G, V = self._makeTree(node, nx.DiGraph(), {node.id: node})
        else:
            G, V = self.G, self.V
        
        pos = nx.drawing.nx_agraph.graphviz_layout(G, prog="dot")
        
        nx.draw_networkx(
            G,
            #ax = ax,
            pos = pos,
            with_labels = False,
            arrows = False,
            node_size = 100,
            node_shape = 'o',
            #node_color = "blue",
        )

        if label == "value":
            labels = { key: value.value for key, value in V.items() }
        else:
            labels = { key: "" for key, valye in V.items() }

        nx.draw_networkx_labels(
            G,
            pos = pos,
            labels = labels,
            font_size = 10,
            #font_color = "magenta",
        )
            


           


