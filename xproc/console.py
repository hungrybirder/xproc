import sys
import argparse
import time
import logging
import signal
from pkg_resources import get_distribution

from xproc import meminfo, vmstat, load, interrupt
from xproc.interrupt import Interrupts
from xproc.util import grouper, cpu_count

logger = logging.getLogger("xproc.console")


def setup_logger(level=logging.INFO):
    # log to stderr
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(fmt="%(message)s", datefmt='%H:%M:%S'))
    console = logging.getLogger("xproc.console")
    console.addHandler(handler)
    console.setLevel(level)


def signal_handler(sig, frame):
    logger.debug("SIG: %s, frame: %s", sig, str(frame))
    logger.info("")
    sys.exit(0)


_SUB_CMD = "sub_cmd"
_CMD_MEM = ["memory", "mem"]
_CMD_VMSTAT = ["vmstat"]
_CMD_PS = ["process", "ps"]
_CMD_VER = ["version"]
_CMD_LOAD = ["load"]
# _CMD_SLABINFO = ["slabinfo"]
_CMD_INTERRUPT = ["interrupt", "int"]


def _add_ps_parser(sub_parsers):
    sub_parsers.add_parser("version", help="Show %(prog)s version")

    ps_parser = sub_parsers.add_parser("process",
                                       aliases=["ps"],
                                       help="TODO process subcommand")
    ps_parser.add_argument("-P", "--pid", type=int, required=True, help="PID")


def _add_mem_parser(sub_parsers):
    mem_parser = sub_parsers.add_parser("memory",
                                        aliases=["mem"],
                                        help="memory subcommand")
    mem_parser.add_argument("--list",
                            action="store_true",
                            help="List Column Names")
    mem_parser.add_argument("-e",
                            "--extra",
                            action="append",
                            type=str,
                            help="Append Memory Column")
    mem_parser.add_argument("interval", nargs='?', default=1, type=int)
    mem_parser.add_argument("count", nargs='?', default=-1, type=int)


def _add_vmstat_parser(sub_parsers):
    vmstat_parser = sub_parsers.add_parser("vmstat", help="vmstat subcommand")
    vmstat_parser.add_argument("--list",
                               action="store_true",
                               help="List Column Names")
    vmstat_parser.add_argument("-e",
                               "--extra",
                               action="append",
                               type=str,
                               help="Append VMStat Column")
    vmstat_parser.add_argument("interval", nargs='?', default=1, type=int)
    vmstat_parser.add_argument("count", nargs='?', default=-1, type=int)


def _add_load_parser(sub_parsers):
    load_parser = sub_parsers.add_parser("load", help="vmstat subcommand")
    load_parser.add_argument("interval", nargs='?', default=1, type=int)
    load_parser.add_argument("count", nargs='?', default=-1, type=int)


def _add_int_parser(sub_parsers):
    int_parser = sub_parsers.add_parser("interrupt",
                                        aliases=["int"],
                                        help="interrupt subcommand")
    int_parser.add_argument("-a",
                            "--all",
                            action="store_true",
                            help="Show every cpu")
    int_parser.add_argument("-f",
                            "--filter",
                            action="append",
                            type=str,
                            help="Filter interrupt")
    int_parser.add_argument("-c",
                            "--cpus",
                            action="append",
                            type=str,
                            help="Display specifed cpus,(e.g. 0,2,4-7)+TOTAL")
    int_parser.add_argument("-l",
                            "--list",
                            action="store_true",
                            help="List interrupt labels")
    int_parser.add_argument("-t",
                            "--top",
                            type=int,
                            default=-1,
                            help="Top N interrupts")
    int_parser.add_argument("interval", nargs='?', default=1, type=int)
    int_parser.add_argument("count", nargs='?', default=-1, type=int)


# def _add_slab_parser(sub_parsers):
#     slab_parser = sub_parsers.add_parser("slabinfo",
#                                          help="slabinfo subcommand")
#     slab_parser.add_argument("--sort",
#                              "-s",
#                              type=str,
#                              choices=["a", "o", "v", "l", "s"],
#                              help="""
#                                 a: active_objs
#                                 o: num_objs
#                                 v: active_slabs
#                                 l: num_slabs
#                                 s: objsize
#                              """)
#     slab_parser.add_argument("--top",
#                              type=int,
#                              default=10,
#                              help="Top N(default=10)")


def parse_argv() -> argparse.Namespace:
    argv = argparse.ArgumentParser("xproc", add_help=False)
    sub_parsers = argv.add_subparsers(required=True,
                                      dest=_SUB_CMD,
                                      help="sub commands")
    _add_ps_parser(sub_parsers)
    _add_mem_parser(sub_parsers)
    _add_vmstat_parser(sub_parsers)
    _add_load_parser(sub_parsers)
    _add_int_parser(sub_parsers)
    try:
        parsed = argv.parse_args()
    except Exception:
        argv.print_help()
        sys.exit(1)
    logger.debug("parsed argv: %s", parsed)
    return parsed


def list_memory_available_column_names():
    minfo = meminfo.MemoryInfo()
    for i in grouper(5, minfo.names()):
        logger.info("\t%s", ' '.join(i))


def list_vmstat_available_column_names():
    for i in grouper(6, vmstat.SUPPORT_VMSATA_NAMES.keys()):
        logger.info("\t%s", ' '.join(i))


def show_version():
    print(get_distribution('xproc'))


def should_print_header(loop: int, interval: int) -> bool:
    if loop == 0:
        return True
    if loop % (interval * 10) == 0:
        return True
    return False


def show_memory(option: argparse.Namespace):
    logger.debug("%s", option)
    if option.list:
        return list_memory_available_column_names()
    count = option.count
    interval = max(option.interval, 1)
    extras = []
    if option.extra:
        for item in option.extra:
            extras.extend([i.strip() for i in item.split(",")])
    loop = 0
    while count != 0:
        count -= 1
        try:
            minfo = meminfo.MemoryInfo()
            attrs = minfo.get_attrs(extras)
            title, data = [], []
            for attr in attrs:
                name, value = attr.name, attr.value
                val_str = str(value)
                width = max(len(name), len(val_str), 12)
                title.append(f"{name:>{width}s}")
                data.append(f"{val_str:>{width}s}")
            if should_print_header(loop, interval):
                logger.info(" ".join(title))
            logger.info(" ".join(data))
        finally:
            loop += 1
            time.sleep(interval)


def show_vmstat(option: argparse.Namespace):
    logger.debug("%s", option)
    if option.list:
        return list_vmstat_available_column_names()
    count = option.count
    interval = max(option.interval, 1)
    extras = []
    if option.extra:
        for item in option.extra:
            extras.extend([i.strip() for i in item.split(",")])
    else:
        extras.extend(vmstat.list_default_vmstat_names())
    loop = 0
    while count != 0:
        count -= 1
        try:
            attrs = vmstat.VMStat().get_attrs(*extras)
            title, data = [], []
            for attr in attrs:
                name, value = attr.name, attr.value
                val_str = str(value)
                width = max(len(name), len(val_str), 12)
                title.append(f"{name:>{width}s}")
                data.append(f"{val_str:>{width}s}")
            if should_print_header(loop, interval):
                logger.info(" ".join(title))
            logger.info(" ".join(data))
        finally:
            loop += 1
            time.sleep(interval)


def show_load(option: argparse.Namespace):
    logger.debug("%s", option)
    count = option.count
    interval = max(option.interval, 1)
    loop = 0
    while count != 0:
        count -= 1
        try:
            attrs = load.current_loadavg().get_attrs()
            title, data = [], []
            for attr in attrs:
                name, value = attr.name, attr.value
                val_str = str(value)
                width = max(len(name), len(val_str), 12)
                title.append(f"{name:>{width}s}")
                data.append(f"{val_str:>{width}s}")
            if should_print_header(loop, interval):
                logger.info(" ".join(title))
            logger.info(" ".join(data))
        finally:
            loop += 1
            time.sleep(interval)


# def show_slabinfo(option: argparse.Namespace):
#     logger.debug("%s", option)
#     sort_by = option.sort
#     top_n = option.top
#     slab_info = slabinfo.current_slabinfo()


def list_int_label(ints: Interrupts):
    title = [f"{'LABEL':>10s}", f"{'NAME':>50s}"]
    logger.info(" ".join(title))
    title = [f"{'-----':>10s}", f"{'----':>50s}"]
    logger.info(" ".join(title))
    for label, name in ints.list_labels():
        data = [f"{label:>10s}", f"{name:>50s}"]
        logger.info(" ".join(data))


def show_interrupt(option: argparse.Namespace):
    logger.debug("%s", option)
    last_ints = interrupt.get()
    if option.list:
        return list_int_label(last_ints)
    count = option.count
    interval = max(option.interval, 1)
    # TODO: top > filter == cpus > all ? 合理吗
    # TODO:找到哪个中断最多
    # TODO:滤某个中断
    # TODO:过滤某个中断，哪个核心最多
    top = option.top
    # cpus = option.cpus
    # fitler = option.filter
    # all = option.all
    # cpu_cnt = cpu_count()
    while count != 0:
        count -= 1
        time.sleep(interval)
        now_ints = interrupt.get()
        delta_ints = now_ints.sub(last_ints)
        last_ints = now_ints
        if top > 0:
            interrupt.show_top(top, interval, logger, delta_ints)
            continue


def main():
    setup_logger()
    signal.signal(signal.SIGINT, signal_handler)
    namespace = parse_argv()
    command = namespace.sub_cmd
    if command in _CMD_VER:
        show_version()
    elif command in _CMD_PS:
        pass
    elif command in _CMD_MEM:
        show_memory(namespace)
    elif command in _CMD_VMSTAT:
        show_vmstat(namespace)
    elif command in _CMD_LOAD:
        show_load(namespace)
    elif command in _CMD_INTERRUPT:
        show_interrupt(namespace)
    # elif command in _CMD_SLABINFO:
    #     show_slabinfo(namespace)
