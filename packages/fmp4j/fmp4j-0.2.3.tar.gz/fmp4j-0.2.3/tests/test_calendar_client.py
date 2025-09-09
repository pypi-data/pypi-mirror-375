from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +-----------------+
# | CALENDAR CLIENT |
# +-----------------+

def test_dividends():
    # given
    symbol = "JNJ"
    client = Fmp4jClient()

    # when
    res = client.dividends(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_dividends_calendar():
    # given
    client = Fmp4jClient()

    # when
    res = client.dividends_calendar()

    # then
    assert res is not None
    assert len(res) > 0

def test_earnings():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.earnings(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_earnings_calendar():
    # given
    client = Fmp4jClient()

    # when
    res = client.earnings_calendar()

    # then
    assert res is not None
    assert len(res) > 0

def test_ipos_calendar():
    # given
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.ipos_calendar(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_ipos_disclosure():
    # given
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.ipos_disclosure(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0

def test_ipos_prospectus():
    # given
    from_date = "2025-02-28"
    to_date = "2025-02-28"
    client = Fmp4jClient()

    # when
    res = client.ipos_prospectus(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0
