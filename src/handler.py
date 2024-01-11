from datetime import datetime

from src.datatype.adt import queue, stack
from src.datatype.web import Site, Href

# USE
from src.inventory import Inventory

# Abstracted Base Class
from src.abc import HandlerBase


class Handler(HandlerBase):
    @property
    def inventory(self):
        return self._inventory
    @inventory.setter
    def inventory(self, value: Inventory):
        if not isinstance(value, Inventory):
            raise TypeError
        self._init_waitlist(value.seed)
        self._init_footprint()
        self._inventory = value

    def __init__(self, inventory: Inventory, *args, **kwargs):
        self.inventory = inventory
        self.reset_status()

    def _init_waitlist(self, seed: str):
        self.waitlist = queue()
        seed = Href(
            source = "SEED",
            target = Site(seed),
            weight = 1,
            score = 0.0,
            isActive = False,
        )
        self.waitlist.enque(seed)

    def _init_footprint(self):
        self.footprint = stack()

    @property
    def isFinished(self):
        return self.waitlist.isEmpty()

    def pop_next(self) -> Href:
        href: Href = self.waitlist.deque()
        return href

    def reset_status(self):
        self.starttime = datetime.now()
        self._init_waitlist(self.inventory.seed)
        self._init_footprint()

    def reset_inventory(self):
        pass

    def update(self, done_href: Href, new_hrefs: [Href]):
        self.update_inventory(done_href)
        self.update_waitlist(new_hrefs)

    def update_waitlist(self, new_hrefs: [Href]):
        # update waitlist
        for new_href in new_hrefs:
            try:
                href = self.inventory.get_edge(new_href.source.url, new_href.target.url)
            except KeyError as e:
                # edgeがないなら、targetのnodeが存在するかを確認する
                try:
                    target = self.inventory.get_node(new_href.target.url)
                except KeyError as e:
                    # nodeがないならwaitlistへ
                    self.waitlist.enque(new_href)
                else:
                    if self.starttime > target.timestamp:
                    # nodeがあって、かつ最新の調査がまだならwaitlistへ
                        self.waitlist.enque(new_href)
                    else:
                    # 最新の調査済みであればedgeへ
                        new_href.target = target
                        self.update_inventory(new_href, update_source=False, update_target=False)
            else:
                # edgeがあるなら、そのedgeのターゲットの調査時刻を
                # 調査開始時点との比較する
                if self.starttime > href.target.timestamp:
                    self.waitlist.enque(href)

    def update_inventory(
        self,
        href: Href,
        update_source:bool = False,
        update_target:bool = True,
    ):
        if href.source == "SEED":
            self.inventory.set_node(href.target)
        else:
            self.inventory.set_edge(
                href,
                update_source = update_source,
                update_target = update_target,
            )

