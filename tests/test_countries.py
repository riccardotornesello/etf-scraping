import gettext
import logging

import pycountry
import pytest

from portfolio_scraper import (
    AmundiItScraper,
    ISharesItScraper,
    VanguardItScraper,
    XtrackersItScraper,
)
from portfolio_scraper.utils.country import country_name_to_alpha_2

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

_iso3166 = gettext.translation(
    "iso3166-1",
    pycountry.LOCALES_DIR,
    languages=["it"],
)


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
    country_column: str = "country"
    country_language: str = "it"

    @pytest.fixture(autouse=True)
    def setup(self, request):
        self.scraper = request.getfixturevalue(self.scraper_fixture)

    def test_all_countries_are_mappable(self):
        raw_holdings = self.scraper._fetch_raw_holdings_by_isin(self.ISIN)
        countries = raw_holdings[self.country_column].dropna().unique()

        # TODO: optimize
        unmapped = {
            c
            for c in countries
            if country_name_to_alpha_2(c, self.country_language)
            and country_name_to_alpha_2(c, self.country_language).startswith(
                "__unknown_"
            )
        }
        assert not unmapped, f"Unmapped countries: {sorted(unmapped)}"


# TODO
# class TestAmundiItScraper(ScraperTestBase):
#     ISIN = "LU1681048804"
#     scraper_fixture = "amundi_scraper"


class TestISharesItScraper(ScraperTestBase):
    ISIN = "IE00B6R52143"
    scraper_fixture = "ishares_scraper"
    country_column = "Area Geografica"
    country_language = "it"


# TODO
# class TestVanguardItScraper(ScraperTestBase):
#     ISIN = "IE00B3XXRP09"
#     scraper_fixture = "vanguard_scraper"


# TODO
# class TestXtrackersItScraper(ScraperTestBase):
#     ISIN = "LU3061478973"
#     scraper_fixture = "xtrackers_scraper"
