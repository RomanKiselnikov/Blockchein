import pytest

from src.apps.blockchain import Blockchain


@pytest.fixture(scope="module")
def init_blockchain():
    return Blockchain()


def test_current_transactions(init_blockchain):
    assert init_blockchain.current_transactions == []


def test_valid_chain(init_blockchain):
    assert type(init_blockchain.create_transaction('roma', 'nail', 200)) == int


def test_current_transactions_len(init_blockchain):
    assert len(init_blockchain.current_transactions) > 0
