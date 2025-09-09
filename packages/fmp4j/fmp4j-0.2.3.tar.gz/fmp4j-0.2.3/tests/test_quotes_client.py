from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +---------------+
# | QUOTES CLIENT |
# +---------------+

def test_full_quote():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.full_quote(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol
    assert res[0].price() is not None

def test_partial_quote():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.partial_quote(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol
    assert res[0].price() is not None

def test_price_change():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.price_change(symbol)

    # then
    assert res is not None
    assert len(res) > 0
