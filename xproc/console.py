# pylint: disable=too-few-public-methods
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=W0703

import sys
import argparse
import time
import logging
from typing import List
import signal
from pkg_resources import get_distribution

from xproc import meminfo, value
from xproc import util as xutil

logger = logging.getLogger("xproc.console")


def setup_logger(level=logging.INFO):
    handler = logging.StreamHandler()  # stderr
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(fmt="%(message)s", datefmt='%H:%M:%S'))
    console = logging.getLogger("xproc.console")
    console.addHandler(handler)
    console.setLevel(level)


def signal_handler(sig, frame):
    logger.info("")
    sys.exit(0)


_SUB_CMD = "sub_cmd"
_CMD_MEM = ["memory", "mem"]
_CMD_PS = ["process", "ps"]
_CMD_VER = ["version"]


def parse_argv() -> argparse.Namespace:
    argv = argparse.ArgumentParser("xproc", add_help=False)

    sub_parsers = argv.add_subparsers(required=True,
                                      dest=_SUB_CMD,
                                      help="sub commands")

    version_parser = sub_parsers.add_parser("version",
                                            help="Show %(prog)s version")

    ps_parser = sub_parsers.add_parser("process",
                                       aliases=["ps"],
                                       help="TODO process subcommand")
    ps_parser.add_argument("-P", "--pid", type=int, required=True, help="PID")

    mem_parser = sub_parsers.add_parser("memory",
                                        aliases=["mem"],
                                        help="memory subcommand")
    # mem_parser.add_argument("--debug",
    #                         action="store_true",
    #                         help="Enable debug mode")
    mem_parser.add_argument("--list",
                            action="store_true",
                            help="List Column Names")
    mem_parser.add_argument("-e",
                            "--extra",
                            action="append",
                            type=str,
                            help="Append Memory Column")
    mem_parser.add_argument("interval", nargs='?', default=1, type=int)
    mem_parser.add_argument("count", nargs='?', default=5, type=int)

    # out_group = mem_parser.add_mutually_exclusive_group()
    # out_group.add_argument("--text", action="store_false")
    # out_group.add_argument("--pretty", action="store_true")
    # out_group.add_argument("--csv",
    #                        type=argparse.FileType("w", encoding="utf-8"))

    try:
        parsed = argv.parse_args()
    except Exception:
        argv.print_help()
        sys.exit(1)
    logger.debug("parsed argv: %s", parsed)
    return parsed


def show_version():
    print(get_distribution('xproc'))


def list_memory_available_column_names():

    minfo = meminfo.MemoryInfo()
    for i in xutil.grouper(5, minfo.names()):
        logger.info("\t%s", ' '.join(i))


def show_memory(option: argparse.Namespace):
    setup_logger()
    logger.debug("%s", option)
    if option.list:
        return list_memory_available_column_names()
    count = option.count
    if count <= 0:
        count = 1
    interval = max(option.interval, 1)
    extras = []
    if option.extra:
        for item in option.extra:
            extras.extend([i.strip() for i in item.split(",")])

    loop = 0
    while count != 0:
        count -= 1
        minfo = meminfo.MemoryInfo()
        attrs = minfo.get_attrs(extras)
        if loop == 0:
            logger.info(" ".join((attr.name_str() for attr in attrs)))
        logger.info(" ".join((attr.value_str() for attr in attrs)))
        loop += 1
        time.sleep(interval)


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
