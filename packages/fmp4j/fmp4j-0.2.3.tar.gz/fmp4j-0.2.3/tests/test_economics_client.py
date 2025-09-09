from fmp4j import Fmp4jClient
import pytest
import time

@pytest.fixture(autouse=True)
def delay_between_tests():
    time.sleep(1)

# +------------------+
# | ECONOMICS CLIENT |
# +------------------+

def test_treasury_rates():
    # given
    client = Fmp4jClient()
    from_date = "2025-02-28"
    to_date = "2025-02-28"

    # when
    res = client.treasury_rates(from_date, to_date)

    # then
    assert res is not None
    assert len(res) > 0
