import re
from typing import NamedTuple


class Loadavg(NamedTuple):
    load_1: float
    load_5: float
    load_15: float
    nr_running: int
    nr_total: int
    last_pid: int


EmptyLoadavg = Loadavg(0, 0, 0, 0, 0, 0)

LOAD_PATTERN = re.compile(r"^(?P<load_1>[0-9]+\.[0-9]+)\s+"
                          r"(?P<load_5>[0-9]+\.[0-9]+)\s+"
                          r"(?P<load_15>[0-9]+\.[0-9]+)\s+"
                          r"(?P<nr_running>[0-9]+)/(?P<nr_total>[0-9]+)\s+"
                          r"(?P<last_pid>[0-9]+)\s?$")


def current_loadavg() -> Loadavg:
    # 0.24 0.16 0.06 1/296 1968353
    with open("/proc/loadavg", mode="r", encoding="utf-8") as load:
        line = load.readlines()[0]
    match = re.match(LOAD_PATTERN, line)
    if not match:
        return EmptyLoadavg
    return Loadavg(load_1=float(match.group("load_1")),
                   load_5=float(match.group("load_5")),
                   load_15=float(match.group("load_15")),
                   nr_running=int(match.group("nr_running")),
                   nr_total=int(match.group("nr_total")),
                   last_pid=int(match.group("last_pid")))
