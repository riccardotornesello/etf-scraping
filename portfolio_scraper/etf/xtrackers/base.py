import pandas as pd

from portfolio_scraper.etf.base import BaseEtfScraper
from portfolio_scraper.utils.country import gen_country_to_alpha_2_map
from portfolio_scraper.utils.dataframe import Column, ColumnType, map_columns
from portfolio_scraper.utils.sector import GICSector


class XtrackersBaseEtfScraper(BaseEtfScraper):
    HOLDINGS_CSV_SEPARATOR = ";"

    COUNTRY_LANGUAGE: str
    HOLDINGS_URL_TEMPLATE: str
    HOLDINGS_COLUMN_NAMES: dict[str, str]
    SECTORS_MAP: dict[str, GICSector]

    def __init__(self):
        super().__init__()

        self.HOLDINGS_COLUMNS: dict[str, Column] = map_columns(
            columns={
                "name": Column(),
                "isin": Column(),
                "weight_in_etf": Column(col_type=ColumnType.NUMERIC),
                "gics_sector": Column(mapper=self.SECTORS_MAP),
                "country_alpha2": Column(
                    mapper=gen_country_to_alpha_2_map(self.COUNTRY_LANGUAGE)
                ),
                "exchange": Column(),
                "currency": Column(),
                "rating": Column(),
            },
            columns_names=self.HOLDINGS_COLUMNS_NAMES,
        )

    def _fetch_raw_listings(self) -> pd.DataFrame:
        raise NotImplementedError

    def _fetch_raw_holdings_by_id(self, isin: str) -> pd.DataFrame:
        return self._fetch_raw_holdings_by_isin(isin)

    def _fetch_raw_holdings_by_isin(self, isin: str) -> pd.DataFrame:
        url = self.HOLDINGS_URL_TEMPLATE.format(isin=isin)
        df = pd.read_csv(url, sep=self.HOLDINGS_CSV_SEPARATOR, encoding="utf-8")
        return df

    def _fetch_raw_holdings_by_ticker(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError
