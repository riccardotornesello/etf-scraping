from scrapers.ishares import ISharesItScraper
from scrapers.vanguard import VanguardItScraper
from scrapers.xtrackers import XtrackersItScraper
from scrapers.base import BaseScraper


def scrape_and_print(isin: str, scraper_class: type[BaseScraper]):
    scraper = scraper_class()
    df = scraper.get_holdings_by_isin(isin)
    print(df.head())
    print(df.columns)
    print(df.loc[0])


def main():
    print("=== ISHARES ===")
    scrape_and_print("IE00BG0J4C88", ISharesItScraper)

    print("=== VANGUARD ===")
    scrape_and_print("IE00BK5BQT80", VanguardItScraper)

    print("=== XTRACKERS ===")
    scrape_and_print("IE0006WW1TQ4", XtrackersItScraper)


if __name__ == "__main__":
    main()
