import os
import urllib.request
from pathlib import Path
import jpype
import jpype.imports
from jpype.types import *
from .version import __version__

def handle_java_exception(e):
    """Print detailed Java exception information"""
    print(f"Exception type: {e.__class__.__name__}")
    print(f"Message: {e.message()}")
    print("Stack trace:")
    print(e.stacktrace())

    # nested exception
    cause = e.getCause()
    if cause:
        print("\nCaused by:")
        print(f"  {cause.getClass().getName()}: {cause.getMessage()}")
        print(cause.stacktrace())

def get_jar_path():
    # Check environment variable first
    env_jar_path = os.environ.get('FMP_JAR_PATH')
    if env_jar_path:
        return env_jar_path

    # Determine cache directory
    home = Path.home()
    cache_dir = home / '.fmp4j' / 'jar'
    cache_dir.mkdir(parents=True, exist_ok=True)

    jar_name = f'fmp4j-{__version__}-all.jar'
    jar_path = cache_dir / jar_name

    # Download if not exists
    if not jar_path.exists():
        maven_url = f"https://repo1.maven.org/maven2/dev/sorn/fmp4j/{__version__}/{jar_name}"
        try:
            print(f"Downloading {jar_name} from Maven Central...")
            urllib.request.urlretrieve(maven_url, jar_path)
            print("Download completed.")
        except Exception as e:
            raise RuntimeError(f"Failed to download JAR from {maven_url}: {e}")

    return str(jar_path)

# Start JVM with downloaded JAR
jar_path = get_jar_path()

if not jpype.isJVMStarted():
    jpype.startJVM(
        "-Djava.awt.headless=true",
        classpath=[jar_path],
        convertStrings=True
    )
    print(f"✅ JVM started with classpath: {jar_path}")

# Alphabetical order
import datetime
from java.time import LocalDate
from java.util import HashSet
from java.util import Optional
from dev.sorn.fmp4j import FmpClient
from dev.sorn.fmp4j.cfg import FmpConfig
from dev.sorn.fmp4j.types import FmpSymbol
from dev.sorn.fmp4j.types.FmpCik import cik as to_cik
from dev.sorn.fmp4j.types.FmpCurrency import currency as to_currency
from dev.sorn.fmp4j.types.FmpCusip import cusip as to_cusip
from dev.sorn.fmp4j.types.FmpInterval import interval as to_interval
from dev.sorn.fmp4j.types.FmpIsin import isin as to_isin
from dev.sorn.fmp4j.types.FmpLimit import limit as to_limit
from dev.sorn.fmp4j.types.FmpPeriod import period as to_period
from dev.sorn.fmp4j.types.FmpSymbol import symbol as to_symbol
from jpype import JImplements, JOverride
from dev.sorn.fmp4j.cfg import FmpConfig

def to_local_date(value):
    if value is None:
        return None
    if isinstance(value, str):
        return LocalDate.parse(value)
    elif isinstance(value, datetime.date):
        return LocalDate.of(value.year, value.month, value.day)
    else:
        raise TypeError(f"Invalid type for date: {type(value)}")

def to_optional(value):
    return Optional.of(value) if value is not None else Optional.empty()

@JImplements(FmpConfig)
class PythonFmpConfig:
    def __init__(self, api_key, base_url):
        self._api_key = api_key
        self._base_url = base_url

    @JOverride
    def fmpApiKey(self):
        return self._api_key

    @JOverride
    def fmpBaseUrl(self):
        return self._base_url

class Fmp4jClient:
    def __init__(self):
        self.client = FmpClient()

    # +-----------------+
    # | CALENDAR CLIENT |
    # +-----------------+

    def dividends(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.calendar().dividends(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def dividends_calendar(self):
        try:
            return self.client.calendar().dividends()
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def earnings(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.calendar().earnings(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def earnings_calendar(self):
        try:
            return self.client.calendar().earnings()
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def ipos_calendar(self, from_date, to_date):
        try:
            from_date = to_optional(to_local_date(from_date))
            to_date = to_optional(to_local_date(to_date))
            return self.client.calendar().ipos(from_date, to_date)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def ipos_disclosure(self, from_date, to_date):
        try:
            from_date = to_optional(to_local_date(from_date))
            to_date = to_optional(to_local_date(to_date))
            return self.client.calendar().disclosures(from_date, to_date)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def ipos_prospectus(self, from_date, to_date):
        try:
            from_date = to_optional(to_local_date(from_date))
            to_date = to_optional(to_local_date(to_date))
            return self.client.calendar().prospectus(from_date, to_date)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +--------------+
    # | CHART CLIENT |
    # +--------------+

    def historical_price_eod_light_chart(self, symbol, from_date, to_date):
        try:
            from_date = to_optional(to_local_date(from_date))
            to_date = to_optional(to_local_date(to_date))
            symbol = to_symbol(symbol)
            return self.client.chart().historicalPriceEodLight(symbol, from_date, to_date)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def historical_price_eod_full_chart(self, symbol, from_date, to_date):
        try:
            from_date = to_optional(to_local_date(from_date))
            to_date = to_optional(to_local_date(to_date))
            symbol = to_symbol(symbol)
            return self.client.chart().historicalPriceEodFull(symbol, from_date, to_date)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def historical_chart(self, symbol, interval, from_date, to_date):
        try:
            symbol = to_symbol(symbol)
            interval = to_interval(interval)
            from_date = to_optional(to_local_date(from_date))
            to_date = to_optional(to_local_date(to_date))
            return self.client.chart().historical(symbol, interval, from_date, to_date)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +----------------+
    # | COMPANY CLIENT |
    # +----------------+

    def company(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.company().bySymbol(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +------------------+
    # | DIRECTORY CLIENT |
    # +------------------+

    def etfs(self):
        try:
            return self.client.directory().etfs()
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def stocks(self):
        try:
            return self.client.directory().stocks()
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +------------------+
    # | ECONOMICS CLIENT |
    # +------------------+

    def treasury_rates(self, from_date, to_date):
        try:
            from_date = to_local_date(from_date)
            to_date = to_local_date(to_date)
            return self.client.economics().treasuryRates(from_date, to_date)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +------------+
    # | ETF CLIENT |
    # +------------+

    def etf_asset_exposure(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.etf().assetExposure(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def etf_country_weightings(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.etf().countryWeightings(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def etf_holdings(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.etf().holdings(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def etf_info(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.etf().info(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def etf_sector_weightings(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.etf().sectorWeightings(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +-------------+
    # | NEWS CLIENT |
    # +-------------+

    def crypto_news(self, symbols):
        try:
            symbol_set = HashSet()
            for symbol in symbols:
                symbol_set.add(to_symbol(symbol))
            return self.client.news().crypto(symbol_set)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def forex_news(self, symbols):
        try:
            symbol_set = HashSet()
            for symbol in symbols:
                symbol_set.add(to_symbol(symbol))
            return self.client.news().forex(symbol_set)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def stock_news(self, symbols):
        try:
            symbol_set = HashSet()
            for symbol in symbols:
                symbol_set.add(to_symbol(symbol))
            return self.client.news().stock(symbol_set)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +---------------+
    # | QUOTES CLIENT |
    # +---------------+

    def full_quote(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.quote().full(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def partial_quote(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.quote().partial(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def price_change(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.quote().priceChange(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +---------------+
    # | SEARCH CLIENT |
    # +---------------+

    def search_by_cik(self, cik):
        try:
            cik = to_cik(cik)
            return self.client.search().byCik(cik)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def search_by_cusip(self, cusip):
        try:
            cusip = to_cusip(cusip)
            return self.client.search().byCusip(cusip)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def search_by_isin(self, isin):
        try:
            isin = to_isin(isin)
            return self.client.search().byIsin(isin)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def search_by_name(self, name):
        try:
            return self.client.search().byName(name)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def search_by_symbol(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.search().bySymbol(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +---------------------------+
    # | SEC FILINGS SEARCH CLIENT |
    # +---------------------------+

    def sec_filings_search(self, symbol, from_date, to_date, page, limit):
        try:
            symbol = to_symbol(symbol)
            from_date = to_local_date(from_date)
            to_date = to_local_date(to_date)
            page = to_optional(page)
            limit = to_optional(to_limit(limit))
            return self.client.secFilingsSearch().bySymbol(symbol, from_date, to_date, page, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    # +-------------------+
    # | STATEMENTS CLIENT |
    # +-------------------+

    def income_statement(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().income(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def income_statement_as_reported(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().incomeAsReported(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def income_statement_growth(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().incomeGrowth(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def income_statement_ttm(self, symbol, limit):
        try:
            symbol = to_symbol(symbol)
            limit = to_optional(to_limit(limit))
            return self.client.statement().incomeTtm(symbol, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def balance_sheet_statement(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().balanceSheet(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def balance_sheet_statement_as_reported(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().balanceSheetAsReported(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def balance_sheet_statement_growth(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().balanceSheetGrowth(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def balance_sheet_statement_ttm(self, symbol, limit):
        try:
            symbol = to_symbol(symbol)
            limit = to_optional(to_limit(limit))
            return self.client.statement().balanceSheetTtm(symbol, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def cash_flow_sheet_statement(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().cashFlow(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def cash_flow_sheet_statement_as_reported(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().cashFlowAsReported(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def cash_flow_sheet_statement_growth(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().cashFlowGrowth(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def cash_flow_sheet_statement_ttm(self, symbol, limit):
        try:
            symbol = to_symbol(symbol)
            limit = to_optional(to_limit(limit))
            return self.client.statement().cashFlowTtm(symbol, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def financial_growth(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().financialGrowth(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def key_metrics(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().keyMetrics(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def key_metrics_ttm(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.statement().keyMetricsTtm(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def ratios(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().ratios(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def ratios_ttm(self, symbol):
        try:
            symbol = to_symbol(symbol)
            return self.client.statement().ratiosTtm(symbol)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def enterprise_values(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().enterpriseValues(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def revenue_geographic_segmentations(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().revenueGeographicSegmentations(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise

    def revenue_product_segmentations(self, symbol, period, limit):
        try:
            symbol = to_symbol(symbol)
            period = to_optional(to_period(period))
            limit = to_optional(to_limit(limit))
            return self.client.statement().revenueProductSegmentations(symbol, period, limit)
        except jpype.JException as e:
            handle_java_exception(e)
            raise
