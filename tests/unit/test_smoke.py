"""Smoke test until the suite defined in specs is implemented."""

from __future__ import annotations


def test_package_importable() -> None:
    """Ensures the installable package resolves on PYTHONPATH."""
    import zenith_ops

    assert callable(zenith_ops.main)
    zenith_ops.main()
