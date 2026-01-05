import contextlib
@contextlib.contextmanager

def atomic_write_file(filename, mode='wb'):
    """Write to a filename atomically.

    First write to a unique tempfile, then rename the tempfile into
    place. Use replace instead of rename to make it atomic on windows as well.
    Use as a context manager:

        with atomic_write_file('file.txt') as f:
            f.write('hello')
    """

    tmp_file = f'{filename}.{os.getpid()}'
    with open(tmp_file, mode) as f:
        yield f

    os.replace(tmp_file, filename)
