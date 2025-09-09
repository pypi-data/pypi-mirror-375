from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +--------------+
# | CHART CLIENT |
# +--------------+

def test_historical_price_eod_light_chart():
    # given
    symbol = "AAPL"
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.historical_price_eod_light_chart(symbol, from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_historical_price_eod_full_chart():
    # given
    symbol = "AAPL"
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.historical_price_eod_full_chart(symbol, from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_historical_chart():
    # given
    symbol = "AAPL"
    interval = "1hour"
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.historical_chart(symbol, interval, from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0
