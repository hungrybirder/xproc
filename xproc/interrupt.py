import os
import re
import time
import logging
from typing import Dict, NamedTuple, List, Optional, Tuple

from xproc.util import open_file

logger = logging.getLogger("xproc.interrupt")


def _cpu_count() -> int:
    cnt = os.cpu_count()
    if cnt:
        return cnt
    return -1


class _Interrupt(NamedTuple):
    label: str
    # every cpu int count
    # the length of cpus is equal to os.cpu_count()
    cpus: List[int]
    # type? edge? name?
    extras: List[str]
    # total int count of this label
    total: int

    def get_name(self) -> str:
        return self.extras[-1]

    def get(self, cpu_idx: int) -> int:
        if 0 <= cpu_idx < _cpu_count():
            return self.cpus[cpu_idx]
        return 0

    def __add__(self, other):
        a_cpu = self.cpus
        b_cpu = self.cpus
        n_cpus = []
        for i, a_cnt in enumerate(a_cpu):
            n_cpus.append(a_cnt + b_cpu[i])
        n_total = self.total + other.total
        return _Interrupt(self.label, n_cpus, self.extras, n_total)

    def __sub__(self, other):
        a_cpu = self.cpus
        b_cpu = self.cpus
        n_cpus = []
        for i, a_cnt in enumerate(a_cpu):
            n_cpus.append(a_cnt - b_cpu[i])
        n_total = self.total - other.total
        return _Interrupt(self.label, n_cpus, self.extras, n_total)


_MAX_INTS_EVER: Dict[str, _Interrupt] = {}


class Interrupts(NamedTuple):
    total_int: int
    ints: List[_Interrupt]
    ts_end: float

    def __sub__(self, other):
        delta_total_int = self.total_int - other.total_int
        delta_ts_end = self.ts_end - other.ts_end
        delta_ints: List[_Interrupt] = []
        for i, s_int in enumerate(self.ints):
            delta_int = s_int - other.ints[i]
            delta_ints.append(delta_int)
        return Interrupts(delta_total_int, delta_ints, delta_ts_end)

    def list_labels(self) -> List[Tuple[str, str]]:
        return [(i.label, i.get_name()) for i in self.ints]


def _parse(line: str) -> Optional[_Interrupt]:
    cols = re.split(r"\s+", line)
    if len(cols) <= 2:    # ignore ERR: MIS:
        return None
    label = cols[0]
    if label[-1] == ":":
        label = label[:-1]
    cpu_count = _cpu_count()
    cpus = []
    for i in range(1, cpu_count + 1):
        cpus.append(int(cols[i]))
    extras = cols[1 + cpu_count:]
    return _Interrupt(label, cpus, extras, sum(cpus))


def get() -> Interrupts:
    with open_file("/proc/interrupts") as proc_ints:
        lines = [l.strip() for l in proc_ints.readlines()]
    total_int = 0
    ints: List[_Interrupt] = []
    for line in lines[1:]:    # pass header
        a_int = _parse(line)
        if a_int:
            total_int += a_int.total
            ints.append(a_int)
    return Interrupts(total_int=total_int, ints=ints, ts_end=time.time())
