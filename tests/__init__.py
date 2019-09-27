import sys


class OnPath:
    """
    Test utility to put a pytest path on the Python search path.
    """

    def __init__(self, path):
        self.path = str(path)

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.path.remove(self.path)
