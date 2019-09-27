import time

from . import OnPath

from limeade.scanning import scan_one


def test_source(tmpdir):
    p = tmpdir / "mod_a.py"
    p.write_text('x = 1', encoding='utf8')

    with OnPath(tmpdir):
        import mod_a

        assert not scan_one(mod_a)

        time.sleep(1)  # TODO: Need a non-time-based way of doing this
        p.write_text('x = 2', encoding='utf8')

        assert scan_one(mod_a)
