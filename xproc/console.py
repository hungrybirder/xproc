import sys
import argparse
import time
import logging
import signal
from pkg_resources import get_distribution

from xproc import meminfo, vmstat, load
from xproc.util import grouper

logger = logging.getLogger("xproc.console")


def setup_logger(level=logging.INFO):
    handler = logging.StreamHandler()    # stderr
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


def parse_argv() -> argparse.Namespace:
    argv = argparse.ArgumentParser("xproc", add_help=False)

    sub_parsers = argv.add_subparsers(required=True,
                                      dest=_SUB_CMD,
                                      help="sub commands")

    sub_parsers.add_parser("version", help="Show %(prog)s version")

    ps_parser = sub_parsers.add_parser("process",
                                       aliases=["ps"],
                                       help="TODO process subcommand")
    ps_parser.add_argument("-P", "--pid", type=int, required=True, help="PID")

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

    # out_group = mem_parser.add_mutually_exclusive_group()
    # out_group.add_argument("--text", action="store_false")
    # out_group.add_argument("--pretty", action="store_true")
    # out_group.add_argument("--csv",
    #                        type=argparse.FileType("w", encoding="utf-8"))
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
    vmstat_parser.add_argument("count", nargs='?', default=5, type=int)

    load_parser = sub_parsers.add_parser("load", help="vmstat subcommand")
    load_parser.add_argument("interval", nargs='?', default=1, type=int)
    load_parser.add_argument("count", nargs='?', default=-1, type=int)

    # slab_parser = sub_parsers.add_parser("slabinfo",
    #                                      help="slabinfo subcommand")
    # slab_parser.add_argument("--sort",
    #                          "-s",
    #                          type=str,
    #                          choices=["a", "o", "v", "l", "s"],
    #                          help="""
    #                             a: active_objs
    #                             o: num_objs
    #                             v: active_slabs
    #                             l: num_slabs
    #                             s: objsize
    #                          """)
    # slab_parser.add_argument("--top",
    #                          type=int,
    #                          default=10,
    #                          help="Top N(default=10)")
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


def show_memory(option: argparse.Namespace):
    setup_logger()
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
            if loop == 0:
                logger.info(" ".join(title))
            logger.info(" ".join(data))
        finally:
            loop += 1
            time.sleep(interval)


def show_vmstat(option: argparse.Namespace):
    setup_logger()
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
            if loop == 0:
                logger.info(" ".join(title))
            logger.info(" ".join(data))
        finally:
            loop += 1
            time.sleep(interval)


def show_load(option: argparse.Namespace):
    setup_logger()
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
            if loop == 0:
                logger.info(" ".join(title))
            logger.info(" ".join(data))
        finally:
            loop += 1
            time.sleep(interval)


# def show_slabinfo(option: argparse.Namespace):
#     setup_logger()
#     logger.debug("%s", option)
#     sort_by = option.sort
#     top_n = option.top
#     slab_info = slabinfo.current_slabinfo()


def main():
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
    # elif command in _CMD_SLABINFO:
    #     show_slabinfo(namespace)
