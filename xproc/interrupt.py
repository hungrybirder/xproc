import re
import time
import logging
from operator import attrgetter
from typing import Dict, NamedTuple, List, Tuple, Union

from xproc.util import open_file, cpu_count


class CountStat(NamedTuple):
    label: str
    count: int = 0

    def __add__(self, other):
        return CountStat(self.label, self.count + other.count)

    def __sub__(self, other):
        return CountStat(self.label, self.count - other.count)


class IntStat(NamedTuple):
    # int number or int str
    label: str
    # int count of ever cpu
    # the length of cpus is equal to os.cpu_count()
    cpus: List[int]
    # type? edge? name?
    extras: List[str]
    # sum(cpus)
    total: int

    def get_name(self) -> str:
        return self.extras[-1]

    def extra_str(self) -> str:
        return " ".join(self.extras)

    def get(self, cpu_idx: int) -> int:
        if 0 <= cpu_idx < cpu_count():
            return self.cpus[cpu_idx]
        return 0

    def sub(self, other: "IntStat", period_secs: float = 1):
        # 计算出每个cpu的平均值
        n_cpus = []
        for a_cpu, b_cpu in zip(self.cpus, other.cpus, strict=True):
            avg = int((a_cpu - b_cpu) // period_secs)
            n_cpus.append(avg)
        n_total = self.total - other.total
        return IntStat(self.label, n_cpus, self.extras, n_total)


_MAX_INTS_EVER: Dict[str, IntStat] = {}


class Interrupts(NamedTuple):
    total_int: int
    stats: List[IntStat]
    err: CountStat
    mis: CountStat
    ts_secs: float

    def sub(self, other: 'Interrupts'):
        delta_total_int = self.total_int - other.total_int
        delta_ts_secs = self.ts_secs - other.ts_secs
        delta_stats: List[IntStat] = []
        delta_err = self.err - other.err
        delta_mis = self.mis - other.mis
        for src, dst in zip(self.stats, other.stats, strict=True):
            delta_stats.append(src.sub(dst, delta_ts_secs))
        return Interrupts(total_int=delta_total_int,
                          stats=delta_stats,
                          err=delta_err,
                          mis=delta_mis,
                          ts_secs=delta_ts_secs)

    def list_labels(self) -> List[Tuple[str, str]]:
        return [(i.label, i.extra_str()) for i in self.stats]

    def sort(self, reverse: bool = True, top: int = -1) -> 'Interrupts':
        sorted_stats = sorted(self.stats,
                              key=attrgetter("total"),
                              reverse=reverse)
        if top > 0:
            top_idx = min(top, len(sorted_stats))
        return Interrupts(total_int=self.total_int,
                          stats=sorted_stats[0:top_idx],
                          err=self.err,
                          mis=self.mis,
                          ts_secs=self.ts_secs)


def _parse(line: str) -> Union[IntStat, CountStat]:
    cols = re.split(r"\s+", line)
    label = cols[0]
    if label[-1] == ":":
        label = label[:-1]
    if label == "ERR":
        return CountStat("ERR", int(cols[1]))
    if label == "MIS":
        return CountStat("MIS", int(cols[1]))
    cpu_cnt = cpu_count()
    cpus = [int(c) for c in cols[1:cpu_cnt + 1]]
    extras = cols[cpu_cnt + 1:]
    return IntStat(label, cpus, extras, sum(cpus))


def get() -> Interrupts:
    """
    Get current /proc/interrupts Stats
    """
    with open_file("/proc/interrupts") as proc_ints:
        lines = [l.strip() for l in proc_ints.readlines()]
    total_int = 0
    stats: List[IntStat] = []
    err = CountStat("ERR")
    mis = CountStat("MIS")
    for line in lines[1:]:    # pass header
        stat = _parse(line)
        label = stat.label
        if isinstance(stat, IntStat):
            total_int += stat.total
            stats.append(stat)
        else:    # CountStat
            if label == "ERR":
                err = stat
            elif label == "MIS":
                mis = stat
    return Interrupts(total_int=total_int,
                      stats=stats,
                      mis=mis,
                      err=err,
                      ts_secs=time.time())


# show functions
def show_top(top: int, interval: int, logger: logging.Logger,
             delta_ints: Interrupts):
    # print header
    title = f"{time.strftime('%H:%M:%S', time.localtime()):>55s}"
    logger.info(title)
    if interval == 1:
        title = [f"{'DEVICE(IRQ)':>55s}", f"{'IRQs/SECOND':11s}"]
    else:
        title = [
            f"{'DEVICE(IRQ)':>55s}",
            f"{'IRQs/SECOND':11s}",
            f"{'TOTAL':>11s}",
        ]
    logger.info(" ".join(title))
    # print data
    top_ints = delta_ints.sort(top=top)
    for stat in top_ints.stats:
        label = stat.label
        label_width = len(stat.label)
        name = f"{stat.extra_str()} ({label:>{label_width}s})"
        if interval == 1:
            line = [f"{name:>55s}", f"{sum(stat.cpus):>11d}"]
        else:
            line = [
                f"{name:>55s}",
                f"{sum(stat.cpus):>11d}",
                f"{stat.total:>11d}",
            ]
        logger.info(" ".join(line))
    logger.info("")
