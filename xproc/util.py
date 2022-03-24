# pylint: disable=too-few-public-methods
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

import itertools


def grouper(size: int, iterable):  # Copy from stackoverflow
    aiter = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(aiter, size))
        if not chunk:
            return
        yield chunk
