import re
from typing import List, NamedTuple, Optional, OrderedDict
import collections
import operator

from xproc.util import open_file
from xproc.value import Attr, IntValue, IntUnitValue, StrValue


class AttrSlab(NamedTuple):
    name: Attr
    active_objs: Attr
    num_objs: Attr
    objsize: Attr
    objperslab: Attr
    pagesperslab: Attr
    limit: Attr
    batchcount: Attr
    sharedfactor: Attr
    active_slabs: Attr
    num_slabs: Attr
    sharedavail: Attr


class Slab(NamedTuple):
    name: str
    active_objs: int    # The number of objects that are currently active (i.e., inuse).
    num_objs: int    # The total number of allocated objects
    objsize: int    # in bytes
    objperslab: int    # The number of objects stored in each slab
    pagesperslab: int    # The number of pages allocated for each slab
    # tunables
    limit: int
    batchcount: int
    sharedfactor: int
    #slabdata
    active_slabs: int    # The number of active slabs
    num_slabs: int    # The total number of slabs
    sharedavail: int

    def to_attrslab(self) -> AttrSlab:
        return AttrSlab(
            name=Attr("NAME", StrValue(self.name)),
            active_objs=Attr("ACTIVE_OBJS", IntValue(self.active_objs)),
            num_objs=Attr("NUM_OBJS", IntValue(self.num_objs)),
            objsize=Attr("OBJ_SIZE", IntUnitValue(self.objsize, "B")),
            objperslab=Attr("OBJ_PER_SLAB", IntValue(self.objperslab)),
            pagesperslab=Attr("PAGES_PER_SLAB", IntValue(self.pagesperslab)),
            limit=Attr("LIMIT", IntValue(self.limit)),
            batchcount=Attr("BATCHCOUNT", IntValue(self.batchcount)),
            sharedfactor=Attr("SHAREDFACTOR", IntValue(self.sharedfactor)),
            active_slabs=Attr("ACTIVE_SLABS", IntValue(self.active_slabs)),
            num_slabs=Attr("NUM_SLABS", IntValue(self.num_slabs)),
            sharedavail=Attr("SHAREDAVAIL", IntValue(self.sharedavail)),
        )


# Copy from `slabtop --help`
# The following are valid sort criteria:
#  a: sort by number of active objects
#  b: sort by objects per slab
#  c: sort by cache size
#  l: sort by number of slabs
#  v: sort by number of active slabs
#  n: sort by name
#  o: sort by number of objects (the default)
#  p: sort by pages per slab
#  s: sort by object size
#  u: sort by cache utilization
_SLAB_SORT_KEYWORD = {
    "a": "active_objs",
    "o": "num_objs",
    "v": "active_slabs",
    "l": "num_slabs",
    "s": "objsize",
}


class SlabInfo:

    def __init__(self, slabs: OrderedDict[str, Slab]):
        self._slabs = slabs
        active_objs = 0
        num_objs = 0
        active_slabs = 0
        num_slabs = 0
        for slab in slabs.values():
            active_objs += slab.active_objs
            num_objs += slab.num_objs
            active_slabs += slab.active_slabs
            num_slabs += slab.num_slabs
        self._active_objs = active_objs
        self._num_objs = num_objs
        self._active_slabs = active_slabs
        self._num_slabs = num_slabs

    def active_objs(self) -> Attr:
        return Attr("ACTIVE_OBJS", IntValue(self._active_objs))

    def num_objs(self) -> Attr:
        return Attr("NUM_OBJS", IntValue(self._num_objs))

    def active_slabs(self) -> Attr:
        return Attr("ACTIVE_SLABS", IntValue(self._active_slabs))

    def num_slabs(self) -> Attr:
        return Attr("NUM_SLABS", IntValue(self._num_slabs))

    def _sort(self, bywhat: str = 'o', top: int = -1) -> List[Slab]:
        slabs = list(self._slabs.values())
        if bywhat not in _SLAB_SORT_KEYWORD:
            return slabs
        attr_name = _SLAB_SORT_KEYWORD[bywhat]
        sorted_slabs = sorted(slabs,
                              key=operator.attrgetter(attr_name),
                              reverse=True)
        if top <= 0:
            return sorted_slabs
        return sorted_slabs[0:min(top, len(sorted_slabs))]

    def sort(self, bywhat: str, top: int) -> List[AttrSlab]:
        attr_slabs = []
        for slab in self._sort(bywhat, top):
            attr_slabs.append(slab.to_attrslab())
        return attr_slabs


_SLAB_PAT = re.compile((
    r"^(?P<name>\w+)\s+(?P<active_objs>\d+)\s+(?P<num_objs>\d+)\s+"
    r"(?P<objsize>\d+)\s+(?P<objperslab>\d+)\s+(?P<pagesperslab>\d+)\s+"
    r":\s+tunables\s+(?P<limit>\d+)\s+(?P<batchcount>\d+)\s+(?P<sharedfactor>\d+)\s+"
    r":\s+slabdata\s+(?P<active_slabs>\d+)\s+(?P<num_slabs>\d+)\s+(?P<sharedavail>\d+)\s+$"
))


def _parse(line: str) -> Optional[Slab]:
    match = _SLAB_PAT.match(line)
    if not match:
        return None
    return Slab(
        match.group("name"),
        int(match.group("active_objs")),
        int(match.group("num_objs")),
        int(match.group("objsize")),
        int(match.group("objperslab")),
        int(match.group("pagesperslab")),
        int(match.group("limit")),
        int(match.group("batchcount")),
        int(match.group("sharedfactor")),
        int(match.group("active_slabs")),
        int(match.group("num_slabs")),
        int(match.group("sharedavail")),
    )


def current_slabinfo() -> SlabInfo:
    with open_file("/proc/slabinfo") as sinfo:
        lines = sinfo.readlines()
    slabs = collections.OrderedDict()
    for line in lines:
        slab = _parse(line)
        if slab:
            slabs[slab.name] = slab
    return SlabInfo(slabs)
