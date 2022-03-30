import itertools


def grouper(size: int, iterable):    # Copy from stackoverflow
    aiter = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(aiter, size))
        if not chunk:
            return
        yield chunk
