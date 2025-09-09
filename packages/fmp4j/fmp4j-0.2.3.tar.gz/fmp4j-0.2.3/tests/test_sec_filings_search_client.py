from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +---------------------------+
# | SEC FILINGS SEARCH CLIENT |
# +---------------------------+

def test_filings_search_by_symbol():
    # given
    symbol = "AAPL"
    from_date = "2024-02-28"
    to_date = "2025-02-28"
    page = 0
    limit = 1
    client = Fmp4jClient()

    # when
    res = client.sec_filings_search(symbol, from_date, to_date, page, limit)

    # then
    assert res is not None
    assert len(res) > 0
