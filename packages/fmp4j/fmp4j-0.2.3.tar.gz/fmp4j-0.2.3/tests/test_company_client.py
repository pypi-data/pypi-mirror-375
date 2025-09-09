from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +----------------+
# | COMPANY CLIENT |
# +----------------+

def test_company():
    # given
    symbol = "AAPL"
    client = Fmp4jClient()

    # when
    res = client.company(symbol)

    # then
    assert res is not None
    assert res[0] is not None
    assert res[0].symbol().value() == symbol
