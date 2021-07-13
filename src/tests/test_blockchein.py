import pytest

from src.apps.blockchain import Blockchain


def test_current_transactions():
    bl = Blockchain()
    assert bl.current_transactions == []
