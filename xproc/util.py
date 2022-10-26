import os
import itertools


def grouper(size: int, iterable):    # Copy from stackoverflow
    a_iter = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(a_iter, size))
        if not chunk:
            return
        yield chunk


def open_file(path: str, mode: str = "r"):
    return open(path, mode=mode, encoding="utf-8")


def cpu_count() -> int:
    cnt = os.cpu_count()
    if cnt:
        return cnt
    return -1
