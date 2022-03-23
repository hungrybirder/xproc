# pylint: disable=too-few-public-methods
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=W0703

import sys
import argparse
from typing import NamedTuple
import logging
from pkg_resources import get_distribution

logger = logging.getLogger("xproc.console")


class MemOption(NamedTuple):
    interval: int
    count: int
    debug: bool = False


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
    mem_parser.add_argument("--debug", action="store_true", help="Debug mode")
    mem_parser.add_argument("interval", nargs='?', default=1)
    mem_parser.add_argument("count", nargs='?', default=1)

    out_group = mem_parser.add_mutually_exclusive_group()
    out_group.add_argument("--text", action="store_false")
    out_group.add_argument("--pretty", action="store_true")
    out_group.add_argument("--csv",
                           type=argparse.FileType("w", encoding="utf-8"))

    try:
        parsed = argv.parse_args()
    except Exception:
        argv.print_help()
        sys.exit(1)
    logger.debug("parsed argv: %s", parsed)
    return parsed


def show_version():
    print(get_distribution('xproc'))


# def show_memory(option: MemOption):
#     pass


def main():
    namespace = parse_argv()
    command = namespace.sub_cmd
    if command in _CMD_VER:
        show_version()
    # elif command in _CMD_PS:
    #     pass
    # elif command in _CMD_MEM:
    #     option = MemOption(interval=namespace.interval,
    #                        count=namespace.count,
    #                        debug=namespace.debug)
    #     show_memory(option)
