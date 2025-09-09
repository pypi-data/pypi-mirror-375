from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +-------------------+
# | STATEMENTS CLIENT |
# +-------------------+

def test_income_statement():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_income_statement_as_reported():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement_as_reported(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_income_statement_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_income_statement_ttm():
    # given
    symbol = "AAPL"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.income_statement_ttm(symbol, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement_as_reported():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement_as_reported(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_balance_sheet_statement_ttm():
    # given
    symbol = "AAPL"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.balance_sheet_statement_ttm(symbol, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_cash_flow_sheet_statement():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_cash_flow_sheet_statement_as_reported():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement_as_reported(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_bcash_flow_sheet_statement_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_cash_flow_sheet_statement_ttm():
    # given
    symbol = "AAPL"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.cash_flow_sheet_statement_ttm(symbol, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_financial_growth():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.financial_growth(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_key_metrics():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.key_metrics(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_key_metrics_ttm():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.key_metrics_ttm(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_ratios():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.ratios(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_ratios_ttm():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.ratios_ttm(symbol)

    # then
    assert res is not None
    assert len(res) > 0

def test_enterprise_values():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.enterprise_values(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_revenue_geographic_segmentations():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.revenue_geographic_segmentations(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0

def test_revenue_product_segmentations():
    # given
    symbol = "AAPL"
    period = "annual"
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.revenue_product_segmentations(symbol, period, limit)

    # then
    assert res is not None
    assert len(res) > 0
