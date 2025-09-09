from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +---------------+
# | SEARCH CLIENT |
# +---------------+

def test_search_by_cik():
    # given
    cik = "0000320193"
    client = Fmp4jClient()

    # when
    res = client.search_by_cik(cik)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].cik().value() == cik

def test_search_by_cusip():
    # given
    cusip = "037833100"
    client = Fmp4jClient()

    # when
    res = client.search_by_cusip(cusip)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].cusip().value() == cusip

def test_search_by_isin():
    # given
    isin = "US0378331005"
    client = Fmp4jClient()

    # when
    res = client.search_by_isin(isin)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].isin().value() == isin

def test_search_by_name():
    # given
    name = "Apple"
    client = Fmp4jClient()

    # when
    res = client.search_by_name(name)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].name() == name + " Inc."

def test_search_by_symbol():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.search_by_symbol(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol
