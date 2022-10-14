
import re
from typing import NamedTuple
from xproc.util import open_file


HIERARCHY_IDX = 0
NUM_CGROUPS_IDX = 1
ENABLED_IDX = 2

CPUSET = 'cpuset'
CPU = 'cpu'
CPUACCT = 'cpuacct'
BLKIO = 'blkio'
MEMORY = 'memory'
DEVICES = 'devices'
FREEZER = 'freezer'
NET_CLS = 'net_cls'
PERF_EVENT = 'perf_event'
NET_PRIO = 'net_prio'
HUGETLB = 'hugetlb'
PIDS = 'pids'
RDMA = 'rdma'

class SubSys(NamedTuple):
    name: str
    hierarchy: int
    num_cgroups: int
    enabled: bool

EmptySubSys = SubSys("EmptySubSys", -1, -1, False)

class CGroups:
    def __init__(self, path: str = '/proc/cgroups'):
        with open_file(path) as cgs:
            lines = [l.strip() for l in cgs.readlines() if not l.startswith("#")]
        sub_sys = {}
        for line in lines:
            parts = re.split(r"\s+", line)
            name = parts[0]
            hierarchy = int(parts[1])
            num_cgroups = int(parts[2])
            enabled = bool(int(parts[3]) == 1)
            sub_sys[name] = SubSys(name, hierarchy, num_cgroups, enabled)
        self._subsys = sub_sys

    def get(self, name:str) -> SubSys:
        return self._subsys.get(name, EmptySubSys)

    @property
    def cpuset(self) -> SubSys:
        return self.get(CPUSET)

    @property
    def cpu(self) -> SubSys:
        return self.get(CPU)

    @property
    def cpuacct(self) -> SubSys:
        return self.get(CPUACCT)

    @property
    def blkio(self) -> SubSys:
        return self.get(BLKIO)

    @property
    def memory(self) -> SubSys:
        return self.get(MEMORY)

    @property
    def devices(self) -> SubSys:
        return self.get(DEVICES)

    @property
    def freezer(self) -> SubSys:
        return self.get(FREEZER)

    @property
    def net_cls(self) -> SubSys:
        return self.get(NET_CLS)

    @property
    def perf_event(self) -> SubSys:
        return self.get(PERF_EVENT)

    @property
    def net_prio(self) -> SubSys:
        return self.get(NET_PRIO)

    @property
    def hugetlb(self) -> SubSys:
        return self.get(HUGETLB)

    @property
    def pids(self) -> SubSys:
        return self.get(PIDS)

    @property
    def rdma(self) -> SubSys:
        return self.get(RDMA)

def current_cgroups() -> CGroups:
    return CGroups()
