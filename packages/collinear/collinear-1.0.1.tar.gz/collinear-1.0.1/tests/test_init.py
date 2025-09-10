"""Test that the package can be imported."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import collinear


def test_import() -> None:
    """Test basic import of the collinear package."""
    assert collinear is not None
