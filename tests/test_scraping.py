import logging
import pytest

from portfolio_scraper import (
    AmundiItScraper,
    ISharesItScraper,
    VanguardItScraper,
    XtrackersItScraper,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


@pytest.fixture(scope="module")
def amundi_scraper():
    return AmundiItScraper()


@pytest.fixture(scope="module")
def ishares_scraper():
    return ISharesItScraper()


@pytest.fixture(scope="module")
def vanguard_scraper():
    return VanguardItScraper()


@pytest.fixture(scope="module")
def xtrackers_scraper():
    return XtrackersItScraper()


class ScraperTestBase:
    ISIN: str
    scraper_fixture: str

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.scraper = request.getfixturevalue(self.scraper_fixture)
        self.result = self.scraper.get_holdings_by_isin(self.ISIN)

    def test_get_holdings_does_not_raise(self):
        pass

    def test_get_holdings_returns_result(self):
        assert self.result is not None

    def test_get_holdings_is_nonempty(self):
        assert len(self.result) > 0


class TestAmundiItScraper(ScraperTestBase):
    ISIN = "LU1681048804"
    scraper_fixture = "amundi_scraper"


class TestISharesItScraper(ScraperTestBase):
    ISIN = "IE00B6R52143"
    scraper_fixture = "ishares_scraper"


class TestVanguardItScraper(ScraperTestBase):
    ISIN = "IE00B3XXRP09"
    scraper_fixture = "vanguard_scraper"


class TestXtrackersItScraper(ScraperTestBase):
    ISIN = "LU3061478973"
    scraper_fixture = "xtrackers_scraper"
