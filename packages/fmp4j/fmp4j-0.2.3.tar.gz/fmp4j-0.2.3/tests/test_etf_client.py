from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +------------+
# | ETF CLIENT |
# +------------+

def test_etf_asset_exposure():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_asset_exposure(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_country_weightings():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_country_weightings(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_holdings():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_holdings(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_info():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_info(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_etf_sector_weightings():
    # given
    symbol = "VOO"
    client = Fmp4jClient()

    # when
    res = client.etf_sector_weightings(symbol)

    # then
    assert res is not None
    assert len(res) > 0
