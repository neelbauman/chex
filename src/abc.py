import abc

from src.datatype.collections import dom2dir
from src.datatype.web import Site, Href

class IndexABC(abc.ABC):
    pass


class HandlerBase(abc.ABC):
    def status_update(
        self,
        sites: [Site],
    ) -> None:
        pass

    def pop_next(self) -> Href:
        pass
