import re
from collections import OrderedDict, defaultdict
from typing import Dict, List, NamedTuple, Tuple
import logging
from xproc.util import open_file

from xproc.value import (
    IntUnitValue,
    parse_int_unit_val,
    parse_int_val,
    DEF_FMT_1,
    DEF_FMT_2,
    Attr,
    EmptyAttr,
    current_time_attr,
)

logger = logging.getLogger("xproc.meminfo")

MEMTOTAL = "MemTotal"
MEMFREE = "MemFree"
MEMAVAILABLE = "MemAvailable"
BUFFERS = "Buffers"
CACHED = "Cached"
SWAPCACHED = "SwapCached"
ACTIVE = "Active"
INACTIVE = "Inactive"
ACTIVEANON = "Active(anon)"
INACTIVEANON = "Inactive(anon)"
ACTIVEFILE = "Active(file)"
INACTIVEFILE = "Inactive(file)"
MLOCKED = "Mlocked"
SWAPTOTAL = "SwapTotal"
SWAPFREE = "SwapFree"
DIRTY = "Dirty"
WRITEBACK = "Writeback"
ANONPAGES = "AnonPages"
MAPPED = "Mapped"
SHMEM = "Shmem"
KRECLAIMABLE = "KReclaimable"
SLAB = "Slab"
SRECLAIMABLE = "SReclaimable"
SUNRECLAIM = "SUnreclaim"
KERNELSTACK = "KernelStack"
PAGETABLES = "PageTables"
NFS_UNSTABLE = "NFS_Unstable"
BOUNCE = "Bounce"
WRITEBACKTMP = "WritebackTmp"
COMMITLIMIT = "CommitLimit"
COMMITTED_AS = "Committed_AS"
VMALLOCTOTAL = "VmallocTotal"
VMALLOCUSED = "VmallocUsed"
VMALLOCCHUNK = "VmallocChunk"
HARDWARECORRUPTED = "HardwareCorrupted"
ANONHUGEPAGES = "AnonHugePages"
SHMEMHUGEPAGES = "ShmemHugePages"
SHMEMPMDMAPPED = "ShmemPmdMapped"
HUGEPAGES_TOTAL = "HugePages_Total"
HUGEPAGES_FREE = "HugePages_Free"
HUGEPAGES_RSVD = "HugePages_Rsvd"
HUGEPAGES_SURP = "HugePages_Surp"
HUGEPAGESIZE = "Hugepagesize"
HUGETLB = "Hugetlb"
DIRECTMAP4K = "DirectMap4k"
DIRECTMAP2M = "DirectMap2M"
DIRECTMAP1G = "DirectMap1G"

ATTR_DICT = {
    MEMTOTAL: [parse_int_unit_val, DEF_FMT_2],
    MEMFREE: [parse_int_unit_val, DEF_FMT_2],
    MEMAVAILABLE: [parse_int_unit_val, DEF_FMT_2],
    BUFFERS: [parse_int_unit_val, DEF_FMT_2],
    CACHED: [parse_int_unit_val, DEF_FMT_2],
    SWAPCACHED: [parse_int_unit_val, DEF_FMT_2],
    ACTIVE: [parse_int_unit_val, DEF_FMT_2],
    INACTIVE: [parse_int_unit_val, DEF_FMT_2],
    ACTIVEANON: [parse_int_unit_val, DEF_FMT_2],
    INACTIVEANON: [parse_int_unit_val, DEF_FMT_2],
    ACTIVEFILE: [parse_int_unit_val, DEF_FMT_2],
    INACTIVEFILE: [parse_int_unit_val, DEF_FMT_2],
    MLOCKED: [parse_int_unit_val, DEF_FMT_2],
    SWAPTOTAL: [parse_int_unit_val, DEF_FMT_2],
    SWAPFREE: [parse_int_unit_val, DEF_FMT_2],
    DIRTY: [parse_int_unit_val, DEF_FMT_2],
    WRITEBACK: [parse_int_unit_val, DEF_FMT_2],
    ANONPAGES: [parse_int_unit_val, DEF_FMT_2],
    MAPPED: [parse_int_unit_val, DEF_FMT_2],
    SHMEM: [parse_int_unit_val, DEF_FMT_2],
    KRECLAIMABLE: [parse_int_unit_val, DEF_FMT_2],
    SLAB: [parse_int_unit_val, DEF_FMT_2],
    SRECLAIMABLE: [parse_int_unit_val, DEF_FMT_2],
    SUNRECLAIM: [parse_int_unit_val, DEF_FMT_2],
    KERNELSTACK: [parse_int_unit_val, DEF_FMT_2],
    PAGETABLES: [parse_int_unit_val, DEF_FMT_2],
    NFS_UNSTABLE: [parse_int_unit_val, DEF_FMT_2],
    BOUNCE: [parse_int_unit_val, DEF_FMT_2],
    WRITEBACKTMP: [parse_int_unit_val, DEF_FMT_2],
    COMMITLIMIT: [parse_int_unit_val, DEF_FMT_2],
    COMMITTED_AS: [parse_int_unit_val, DEF_FMT_2],
    VMALLOCTOTAL: [parse_int_unit_val, DEF_FMT_2],
    VMALLOCUSED: [parse_int_unit_val, DEF_FMT_2],
    VMALLOCCHUNK: [parse_int_unit_val, DEF_FMT_2],
    HARDWARECORRUPTED: [parse_int_unit_val, DEF_FMT_2],
    ANONHUGEPAGES: [parse_int_unit_val, DEF_FMT_2],
    SHMEMHUGEPAGES: [parse_int_unit_val, DEF_FMT_2],
    SHMEMPMDMAPPED: [parse_int_unit_val, DEF_FMT_2],
    HUGEPAGES_TOTAL: [parse_int_val, DEF_FMT_1],
    HUGEPAGES_FREE: [parse_int_val, DEF_FMT_1],
    HUGEPAGES_RSVD: [parse_int_val, DEF_FMT_1],
    HUGEPAGES_SURP: [parse_int_val, DEF_FMT_1],
    HUGEPAGESIZE: [parse_int_unit_val, DEF_FMT_2],
    HUGETLB: [parse_int_unit_val, DEF_FMT_2],
    DIRECTMAP4K: [parse_int_unit_val, DEF_FMT_2],
    DIRECTMAP2M: [parse_int_unit_val, DEF_FMT_2],
    DIRECTMAP1G: [parse_int_unit_val, DEF_FMT_2],
}


class MemoryInfo:

    def __init__(self, path="/proc/meminfo"):
        with open(path, mode="r", encoding="utf-8") as meminfo:
            lines = meminfo.readlines()
        attrs: Dict[str, Attr] = OrderedDict()
        for line in lines:
            sep_idx = line.find(":")
            name = line[0:sep_idx]
            val = line[sep_idx + 1:-1]    # exclude \n
            if name not in ATTR_DICT:
                continue
            parser, fmt = ATTR_DICT[name]
            attr = parser(name, val)
            attr.set_value_fmt(fmt)
            attrs[name] = attr
        self._attrs = attrs
        kernel = self._get_kernel_used_mem()
        self._attrs[kernel.name] = kernel
        user = self._get_user_used_mem()
        self._attrs[user.name] = user

    def _get_attr(self, name: str) -> Attr:
        if name not in self._attrs:
            return EmptyAttr
        return self._attrs[name]

    def get_attr_int_value(self, name: str) -> int:
        attr = self._get_attr(name)
        val = attr.value.value()
        if isinstance(val, int):
            return val
        return 0

    def names(self) -> List[str]:
        return list(self._attrs.keys())

    def _get_kernel_used_mem(self) -> Attr:
        """
        From http://linuxperf.com/?cat=7
        Kernel Used Memory includes:
            1. Slab
            2. VmallocUsed
            3. PageTables
            4. KernelStack
            5. HardwareCorrupted
            6. Bounce
            7. X, alloc_pages/__get_free_pages, but not in /proc/meminfo
        """
        slab = self._get_attr(SLAB)
        vmalloc_used = self._get_attr(VMALLOCUSED)
        page_tables = self._get_attr(PAGETABLES)
        kernel_stack = self._get_attr(KERNELSTACK)
        hw_corrupted = self._get_attr(HARDWARECORRUPTED)
        bounce = self._get_attr(BOUNCE)
        logger.debug("Kernel Used Memory Details, %s, %s, %s, %s, %s, %s",
                     slab, vmalloc_used, page_tables, kernel_stack,
                     hw_corrupted, bounce)
        used = [
            slab.value.value(),
            vmalloc_used.value.value(),
            page_tables.value.value(),
            kernel_stack.value.value(),
            hw_corrupted.value.value(),
            bounce.value.value(),
        ]
        kernel_used = 0
        for val in used:
            if isinstance(val, int):
                kernel_used += val
        kval = IntUnitValue(kernel_used, "kB")
        kval.fmt = DEF_FMT_2
        logger.debug("Total Kernel Used Memory: %d %s", kval.value(),
                     kval.unit())
        return Attr("KERNEL", kval)

    def _get_user_used_mem(self) -> Attr:
        """
        From http://linuxperf.com/?cat=7
        User Used Memory includes:
            1. Cached
            2. AnonPages
            3. Buffers
            4. HugePages_Total * Hugepagesize

        > 用户进程的内存主要有三种统计口径：
        >   1. 围绕LRU进行统计
        >     【(Active + Inactive + Unevictable) + (HugePages_Total * Hugepagesize)】
        >   2. 围绕Page Cache进行统计
        >     当SwapCached为0的时候，用户进程的内存总计如下：
        >     【(Cached + AnonPages + Buffers) + (HugePages_Total * Hugepagesize)】
        >     当SwapCached不为0的时候，以上公式不成立，因为SwapCached可能会含有Shmem，
        >     而Shmem本来被含在Cached中，一旦swap-out就从Cached转移到了SwapCached，
        >     可是我们又不能把SwapCached加进上述公式中，
        >     因为SwapCached虽然不与Cached重叠却与AnonPages有重叠，
        >     它既可能含有Shared memory又可能含有Anonymous Pages。
        >   3. 围绕RSS/PSS进行统计
        >     把/proc/[1-9]*/smaps 中的 Pss 累加起来就是所有用户进程占用的内存，
        >     但是还没有包括Page Cache中unmapped部分、以及HugePages，所以公式如下：
        >     ΣPss + (Cached – mapped) + Buffers + (HugePages_Total * Hugepagesize)
        """
        cached = self._get_attr(CACHED)
        anon_pages = self._get_attr(ANONPAGES)
        buffers = self._get_attr(BUFFERS)
        hp_total = self.get_attr_int_value(HUGEPAGES_TOTAL)
        hp_size = self.get_attr_int_value(HUGEPAGESIZE)
        logger.debug("User Used Memory Details, %s, %s, %s, %d, %d", cached,
                     anon_pages, buffers, hp_total, hp_size)
        used = [
            cached.value.value(),
            anon_pages.value.value(),
            buffers.value.value(),
            hp_total * hp_size,
        ]
        user_used = 0
        for val in used:
            if isinstance(val, int):
                user_used += val
        uval = IntUnitValue(user_used, "kB")
        uval.fmt = DEF_FMT_2
        logger.debug("Total User Used Memory: %d %s", uval.value(),
                     uval.unit())
        return Attr("USER", uval)

    def get_attrs(self, names: List[str]) -> List[Attr]:
        attrs = []
        attrs.append(current_time_attr())
        if not names:
            names = ["KERNEL", "USER", MEMFREE, MEMTOTAL]
        if names:
            for name in names:
                attr = self._get_attr(name)
                if attr and attr != EmptyAttr:
                    attrs.append(attr)
        return attrs

    def get_attr(self, name: str) -> Attr:
        return self._get_attr(name)


class Vmalloc(NamedTuple):
    vaddr_start: int
    vaddr_end: int
    size_in_bytes: int
    caller: str
    # optional fields
    pages: int = 0    # number of pages
    phys: int = 0    # physical address
    ioremap: bool = False    # I/O mapping (ioremap() and friends)
    vmalloc: bool = False    # vmalloc() area
    vmap: bool = False    # vmap()ed pages
    user: bool = False    # VM_USERMAP area
    vpages: bool = False    # buffer for pages pointers was vmalloced (huge area)
    npages_on_memory_node: Dict[str, int] = {}
    tag: str = ""


EmptyVmalloc = Vmalloc(0, 0, 0, "")


class VmallocInfo:

    PAGES_PAT = re.compile(r"^pages=(?P<pages>\d+)$")

    NODE_PAT = re.compile(r"^N(?P<index>\d)=(?P<pages>\d+)$")

    PHYS_PAT = re.compile(r"phys=(?P<addr>\d+)")

    TAG_PAT = re.compile(r"^(?P<tag>\[\w+\])$")

    UNPURGED = "unpurged"
    IOREMAP = "ioremap"
    VMALLOC = "vmalloc"
    VMAP = "vmap"
    USER = "user"
    VPAGES = "vpages"

    @staticmethod
    def _parse(line: str) -> Vmalloc:
        # pylint: disable=too-many-locals,too-many-statements
        # https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst#vmallocinfo
        units = re.split(r"\s+", line)
        addr_range = units[0]
        idx = addr_range.find("-")
        start = int(addr_range[0:idx], base=16)
        end = int(addr_range[idx + 1:], base=16)
        size = int(units[1])
        if end - start != size:
            logger.error("end(%d) - start(%d) != size(%d)", end, start, size)
        caller = units[2]
        if caller == VmallocInfo.UNPURGED:
            return Vmalloc(start, end, size, VmallocInfo.UNPURGED)
        # parse optional
        pages = 0
        phys = 0
        ioremap = False
        vmalloc = False
        vmap = False
        user = False
        vpages = False
        npages_on_memory_node: Dict[str, int] = {}
        tag = ""
        for unit in units[3:]:
            match = VmallocInfo.TAG_PAT.match(unit)
            if match:
                tag = match.group("tag")
                continue
            match = VmallocInfo.PAGES_PAT.match(unit)
            if match:
                pages = int(match.group("pages"))
                continue
            match = VmallocInfo.PHYS_PAT.match(unit)
            if match:
                phys = int(match.group("addr"), base=16)
                continue
            if unit == VmallocInfo.IOREMAP:
                ioremap = True
                continue
            if unit == VmallocInfo.VMALLOC:
                vmalloc = True
                continue
            if unit == VmallocInfo.VMAP:
                vmap = True
                continue
            if unit == VmallocInfo.USER:
                user = True
                continue
            if unit == VmallocInfo.VPAGES:
                vpages = True
                continue
            match = VmallocInfo.NODE_PAT.match(unit)
            if match:
                node_idx = match.group("index")
                node_pages = match.group("pages")
                npages_on_memory_node[f"N{node_idx}"] = int(node_pages)
                continue
        return Vmalloc(start, end, size, caller, pages, phys, ioremap, vmalloc,
                       vmap, user, vpages, npages_on_memory_node, tag)

    def __init__(self, path="/proc/vmallocinfo"):
        with open_file(path) as vminfo:
            lines = [l.strip() for l in vminfo.readlines()]
        vms = []
        for line in lines:
            vmalloc = VmallocInfo._parse(line)
            if vmalloc != EmptyVmalloc:
                vms.append(vmalloc)
        self._vmallocs = vms
        callers = defaultdict(list)
        for vmalloc in vms:
            callers[vmalloc.caller].append(vmalloc)
        self._callers: Dict[str, List[Vmalloc]] = callers
        by_size: List[Tuple[str, int]] = []
        for cname, clist in self._callers.items():
            csize = 0
            for cvm in clist:
                csize += cvm.size_in_bytes
            by_size.append((cname, csize))
        self._sorted_by_size = sorted(by_size,
                                      key=lambda pair: pair[1],
                                      reverse=True)
