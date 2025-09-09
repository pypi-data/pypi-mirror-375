from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +------------------+
# | DIRECTORY CLIENT |
# +------------------+

def test_etfs():
    # given
    client = Fmp4jClient()

    # when
    res = client.etfs()

    # then
    assert res is not None
    assert len(res) > 0

def test_stocks():
    # given
    client = Fmp4jClient()

    # when
    res = client.etfs()

    # then
    assert res is not None
    assert len(res) > 0
