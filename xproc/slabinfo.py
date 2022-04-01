import re
from typing import List, NamedTuple, Optional, OrderedDict
import collections

from xproc.util import open_file


class Slab(NamedTuple):
    name: str
    active_objs: int
    num_objs: int
    obj_size: int
    objperslab: int
    pagesperslab: int
    # tunables
    limit: int
    batchcount: int
    sharedfactor: int
    #slabdata
    active_slabs: int
    num_slabs: int
    sharedavail: int


class SlabInfo(NamedTuple):
    slabs: OrderedDict[str, Slab]

    def names(self) -> List[str]:
        return list(self.slabs.keys())

    def find(self, slab_name: str) -> Optional[Slab]:
        return self.slabs.get(slab_name, None)


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
