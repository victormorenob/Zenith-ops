"""Sanity check: package importable and CLI entrypoint exists."""

import zenith_ops


def test_package_importable() -> None:
    assert hasattr(zenith_ops, "main")


def test_main_runs() -> None:
    # Solo ejecutamos para ver que no explote
    zenith_ops.main()
