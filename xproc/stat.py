from typing import NamedTuple, List

from xproc.value import (
    Attr,
    parse_list_int_val,
    ListIntValue,
)


class CPUStat(NamedTuple):
    user: int
    nice: int
    system: int
    idle: int
    iowait: int
    irq: int
    softirq: int
    steal: int
    guest: int
    guest_nice: int


EmptyCpuStat = CPUStat(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


class SoftIRQStat(NamedTuple):
    total: int
    hi: int
    timer: int
    net_tx: int
    net_rx: int
    block: int
    irq_poll: int
    tasklet: int
    sched: int
    hrtimer: int
    rcu: int


EmptySoftIRQStat = SoftIRQStat(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


class SystemStat(NamedTuple):
    cpu: CPUStat
    cpus: List[CPUStat]
    intr: List[int]
    ctxt: int
    btime_in_sec: int
    processes: int
    procs_running: int
    procs_blocked: int
    softirq: SoftIRQStat


def _parse_cpustat(attr: Attr) -> CPUStat:
    if isinstance(attr.value, ListIntValue):
        return CPUStat(*attr.value.value())
    return EmptyCpuStat


def current_system_stat(path="/proc/stat"):
    with open(path, "r", encoding="utf-8") as stat:
        lines = stat.readlines()
    attrs: List[Attr] = []
    for line in lines:
        line = line.strip()
        idx = line.find(" ")
        name = line[0:idx]
        value = line[idx + 1:]
        attrs.append(parse_list_int_val(name, value))
    cpus = []
    d_other = {}
    i_other = {}
    softirq = []
    for attr in attrs:
        name = attr.name
        if name.startswith("cpu"):
            cpus.append(_parse_cpustat(attr))
        elif name.startswith("intr"):
            value = attr.value
            if isinstance(value, ListIntValue):
                d_other[name] = value.value()
        elif name.startswith("softirq"):
            value = attr.value
            if isinstance(value, ListIntValue):
                softirq = value.value()
        else:
            value = attr.value
            if isinstance(value, ListIntValue):
                i_other[name] = value.value()[0]
    return SystemStat(cpus[0], cpus[1:], d_other["intr"], i_other["ctxt"],
                      i_other["btime"], i_other["processes"],
                      i_other["procs_running"], i_other["procs_blocked"],
                      SoftIRQStat(*softirq))
