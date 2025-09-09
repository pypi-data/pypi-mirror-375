from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +-------------+
# | NEWS CLIENT |
# +-------------+

def test_crypto_news():
    # given
    symbol = "BTCUSD"
    client = Fmp4jClient()

    # when
    # res = client.crypto_news(symbol)

    # then
    # assert res is not None
    # assert len(res) > 0

def test_forex_news():
    # given
    symbol = "EURUSD"
    client = Fmp4jClient()

    # when
    # res = client.forex_news(symbol)

    # then
    # assert res is not None
    # assert len(res) > 0

def test_stock_news():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    # res = client.stock_news(symbol)

    # then
    # assert res is not None
    # assert len(res) > 0
