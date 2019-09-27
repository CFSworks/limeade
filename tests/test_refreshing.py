import time

from . import OnPath

import limeade

TEST_MODULE = """\
class X:
    def foo(self):
        return 1

def foo():
    return 1

x = 1
"""


def test_refresh_mutate(tmpdir):
    p = tmpdir / "mod_b.py"
    p.write_text(TEST_MODULE, encoding='utf8')

    with OnPath(tmpdir):
        import mod_b

        assert mod_b.x == 1
        assert mod_b.foo() == 1

        x = mod_b.X()
        assert x.foo() == 1

        time.sleep(1.0)
        p.write_text(TEST_MODULE.replace('1', '2'), encoding='utf8')

        limeade.refresh([mod_b], mutate=True)

        assert mod_b.x == 2
        assert mod_b.foo() == 2

        assert x.foo() == 2
