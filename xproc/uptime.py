from typing import NamedTuple

from xproc.util import open_file


class Uptime(NamedTuple):
    since_boot_in_seconds: float
    idle_seconds: float


def current_uptime() -> Uptime:
    with open_file("/proc/uptime") as uptime:
        line = uptime.readlines()[0].strip()
    units = line.split(" ")
    return Uptime(float(units[0]), float(units[1]))
