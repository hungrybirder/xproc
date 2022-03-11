# pylint: disable=too-few-public-methods
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import Dict, List
import pathlib
import re

PID_PAT = re.compile(r"[1-9][0-9]+")

DEF_FMT_1 = "{0}"
DEF_FMT_2 = "{0} {1}"


class AttrValue(metaclass=ABCMeta):
    """Attr Value"""

    def __init__(self):
        self._fmt = DEF_FMT_1

    @property
    def fmt(self):
        return self._fmt

    @fmt.setter
    def fmt(self, value):
        self._fmt = value

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def format_value(self, fmt: str) -> str:
        pass


class IntValue(AttrValue):

    def __init__(self, val: int):
        super().__init__()
        self.val = val

    def value(self):
        return self.val

    def format_value(self, fmt: str) -> str:
        return fmt.format(self.val)

    def __repr__(self) -> str:
        return self.fmt.format(self.val)


class StrValue(AttrValue):

    def __init__(self, val: str):
        super().__init__()
        self.val = val

    def value(self):
        return self.val

    def format_value(self, fmt: str) -> str:
        return fmt.format(self.val)

    def __repr__(self) -> str:
        return self.fmt.format(self.val)


class IntUnitValue(IntValue):

    def __init__(self, val: int, unit: str):
        super().__init__(val)
        self.unit = unit

    def value(self):
        return self.val

    def format_value(self, fmt: str) -> str:
        return fmt.format(self.val, self.unit)

    def __repr__(self) -> str:
        return self.fmt.format(self.val, self.unit)


class Attr:

    def __init__(self, name, value: AttrValue):
        self._name = name
        self._value = value

    def __repr__(self) -> str:
        return f"{self._name}:{self._value}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def value_str(self) -> str:
        return str(self._value)

    def set_value_fmt(self, fmt: str):
        self._value.fmt = fmt


def parse_int_val(name: str, value: str) -> Attr:
    return Attr(name, IntValue(int(value.strip())))


def parse_int_unit_val(name: str, value: str) -> Attr:
    values = value.strip().split(" ")
    return Attr(name, IntUnitValue(int(values[0]), values[1]))


def parse_str_val(name: str, value: str) -> Attr:
    return Attr(name, StrValue(value.strip()))


PS_NAME = "Name"
PS_UMASK = "Umask"
PS_STATE = "State"
PS_TGID = "Tgid"
PS_NGID = "Ngid"
PS_PID = "Pid"
PS_PPID = "PPid"
PS_TRACERPID = "TracerPid"
PS_UID = "Uid"
PS_GID = "Gid"
PS_FDSIZE = "FDSize"
PS_GROUPS = "Groups"
PS_NSTGID = "NStgid"
PS_NSPID = "NSpid"
PS_NSPGID = "NSpgid"
PS_NSSID = "NSsid"
PS_VMPEAK = "VmPeak"
PS_VMSIZE = "VmSize"
PS_VMLCK = "VmLck"
PS_VMPIN = "VmPin"
PS_VMHWM = "VmHWM"
PS_VMRSS = "VmRSS"
PS_RSSANON = "RssAnon"
PS_RSSFILE = "RssFile"
PS_RSSSHMEM = "RssShmem"
PS_VMDATA = "VmData"
PS_VMSTK = "VmStk"
PS_VMEXE = "VmExe"
PS_VMLIB = "VmLib"
PS_VMPTE = "VmPTE"
PS_VMSWAP = "VmSwap"
PS_HUGETLBPAGES = "HugetlbPages"
PS_COREDUMPING = "CoreDumping"
PS_THP_ENABLED = "THP_enabled"
PS_THREADS = "Threads"
PS_SIGQ = "SigQ"
PS_SIGPND = "SigPnd"
PS_SHDPND = "ShdPnd"
PS_SIGBLK = "SigBlk"
PS_SIGIGN = "SigIgn"
PS_SIGCGT = "SigCgt"
PS_CAPINH = "CapInh"
PS_CAPPRM = "CapPrm"
PS_CAPEFF = "CapEff"
PS_CAPBND = "CapBnd"
PS_CAPAMB = "CapAmb"
PS_NONEWPRIVS = "NoNewPrivs"
PS_SECCOMP = "Seccomp"
PS_SPECULATION_STORE_BYPASS = "Speculation_Store_Bypass"
PS_CPUS_ALLOWED = "Cpus_allowed"
PS_CPUS_ALLOWED_LIST = "Cpus_allowed_list"
PS_MEMS_ALLOWED = "Mems_allowed"
PS_MEMS_ALLOWED_LIST = "Mems_allowed_list"
PS_VOLUNTARY_CTXT_SWITCHES = "voluntary_ctxt_switches"
PS_NONVOLUNTARY_CTXT_SWITCHES = "nonvoluntary_ctxt_switches"

ATTR_DICT = {
    PS_NAME: [parse_str_val, DEF_FMT_1],
    PS_UMASK: [parse_str_val, DEF_FMT_1],
    PS_STATE: [parse_str_val, DEF_FMT_1],
    PS_TGID: [parse_int_val, DEF_FMT_1],
    PS_NGID: [parse_int_val, DEF_FMT_1],
    PS_PID: [parse_int_val, DEF_FMT_1],
    PS_PPID: [parse_int_val, DEF_FMT_1],
    PS_TRACERPID: [parse_int_val, DEF_FMT_1],
    PS_UID: [parse_str_val, DEF_FMT_1],
    PS_GID: [parse_str_val, DEF_FMT_1],
    PS_FDSIZE: [parse_int_val, DEF_FMT_1],
    PS_GROUPS: [parse_str_val, DEF_FMT_1],
    PS_NSTGID: [parse_int_val, DEF_FMT_1],
    PS_NSPID: [parse_int_val, DEF_FMT_1],
    PS_NSPGID: [parse_int_val, DEF_FMT_1],
    PS_NSSID: [parse_int_val, DEF_FMT_1],
    PS_VMPEAK: [parse_int_unit_val, DEF_FMT_2],
    PS_VMSIZE: [parse_int_unit_val, DEF_FMT_2],
    PS_VMLCK: [parse_int_unit_val, DEF_FMT_2],
    PS_VMPIN: [parse_int_unit_val, DEF_FMT_2],
    PS_VMHWM: [parse_int_unit_val, DEF_FMT_2],
    PS_VMRSS: [parse_int_unit_val, DEF_FMT_2],
    PS_RSSANON: [parse_int_unit_val, DEF_FMT_2],
    PS_RSSFILE: [parse_int_unit_val, DEF_FMT_2],
    PS_RSSSHMEM: [parse_int_unit_val, DEF_FMT_2],
    PS_VMDATA: [parse_int_unit_val, DEF_FMT_2],
    PS_VMSTK: [parse_int_unit_val, DEF_FMT_2],
    PS_VMEXE: [parse_int_unit_val, DEF_FMT_2],
    PS_VMLIB: [parse_int_unit_val, DEF_FMT_2],
    PS_VMPTE: [parse_int_unit_val, DEF_FMT_2],
    PS_VMSWAP: [parse_int_unit_val, DEF_FMT_2],
    PS_HUGETLBPAGES: [parse_int_unit_val, DEF_FMT_2],
    PS_COREDUMPING: [parse_int_val, DEF_FMT_1],
    PS_THP_ENABLED: [parse_int_val, DEF_FMT_1],
    PS_THREADS: [parse_int_val, DEF_FMT_1],
    PS_SIGQ: [parse_str_val, DEF_FMT_1],
    PS_SIGPND: [parse_str_val, DEF_FMT_1],
    PS_SHDPND: [parse_str_val, DEF_FMT_1],
    PS_SIGBLK: [parse_str_val, DEF_FMT_1],
    PS_SIGIGN: [parse_str_val, DEF_FMT_1],
    PS_SIGCGT: [parse_str_val, DEF_FMT_1],
    PS_CAPINH: [parse_str_val, DEF_FMT_1],
    PS_CAPPRM: [parse_str_val, DEF_FMT_1],
    PS_CAPEFF: [parse_str_val, DEF_FMT_1],
    PS_CAPBND: [parse_str_val, DEF_FMT_1],
    PS_CAPAMB: [parse_str_val, DEF_FMT_1],
    PS_NONEWPRIVS: [parse_int_val, DEF_FMT_1],
    PS_SECCOMP: [parse_int_val, DEF_FMT_1],
    PS_SPECULATION_STORE_BYPASS: [parse_str_val, DEF_FMT_1],
    PS_CPUS_ALLOWED: [parse_str_val, DEF_FMT_1],
    PS_CPUS_ALLOWED_LIST: [parse_str_val, DEF_FMT_1],
    PS_MEMS_ALLOWED: [parse_str_val, DEF_FMT_1],
    PS_MEMS_ALLOWED_LIST: [parse_str_val, DEF_FMT_1],
    PS_VOLUNTARY_CTXT_SWITCHES: [parse_int_val, DEF_FMT_1],
    PS_NONVOLUNTARY_CTXT_SWITCHES: [parse_int_val, DEF_FMT_1],
}


class PIDStatus:

    def __init__(self, pid: int):
        status_path = f"/proc/{pid}/status"
        with open(status_path, mode="r", encoding="UTF-8") as status_fp:
            lines = status_fp.readlines()
        attrs: Dict[str, Attr] = OrderedDict()
        for line in lines:
            sep_idx = line.find(":")
            name = line[0:sep_idx]
            val = line[sep_idx + 1:-1]  # exclude \n
            if name not in ATTR_DICT:
                continue
            parser, fmt = ATTR_DICT[name]
            attr = parser(name, val)
            attr.set_value_fmt(fmt)
            attrs[name] = attr
        self._attrs = attrs

    def get(self, name: str) -> str:
        if name not in self._attrs:
            return ""
        attr = self._attrs[name]
        return str(attr)

    def names(self) -> List[str]:
        return list(self._attrs.keys())


def get_all_pidstatus() -> Dict[int, PIDStatus]:
    pids = {}
    proc_path = pathlib.Path("/proc")
    for process_path in proc_path.glob("*"):
        if process_path.is_dir() and re.match(PID_PAT, process_path.name):
            pid = int(process_path.name)
            pids[pid] = PIDStatus(pid)
    return pids
