import pandas as pd

from portfolio_scraper.etf.base import BaseEtfScraper
from portfolio_scraper.utils.dataframe import Column, ColumnType, map_columns
from portfolio_scraper.utils.country import gen_country_to_alpha_2_map
from portfolio_scraper.utils.sector import GICSector


class ISharesBaseEtfScraper(BaseEtfScraper):
    COUNTRY_LANGUAGE: str
    LISTINGS_URL: str
    HOLDINGS_URL_TEMPLATE: str

    LISTINGS_COLUMNS_NAMES: dict[str, str]
    HOLDINGS_COLUMNS_NAMES: dict[str, str]
    SECTORS_MAP: dict[str, GICSector]

    HOLDINGS_CSV_SEPARATOR = ","
    HOLDINGS_CSV_THOUSANDS = "."
    HOLDINGS_CSV_DECIMAL = ","

    def __init__(self):
        super().__init__()

        self.LISTINGS_COLUMNS: dict[str, Column] = map_columns(
            columns={
                "internal_id": Column(),
                "name": Column(),
                "isin": Column(),
                "ticker": Column(),
                "ter": Column(
                    formatter=lambda column: column.apply(
                        lambda value: value["r"] if isinstance(value, dict) else None
                    ),
                ),
            },
            columns_names=self.LISTINGS_COLUMNS_NAMES,
        )

        self.HOLDINGS_COLUMNS: dict[str, Column] = map_columns(
            columns={
                "name": Column(),
                "ticker": Column(),
                "weight_in_etf": Column(
                    col_type=ColumnType.NUMERIC,
                    formatter=lambda column: (
                        column.str.replace("%", "", regex=False)
                        .str.replace(".", "", regex=False)
                        .str.replace(",", ".", regex=False)
                        .str.strip()
                        .astype(float)
                        .div(100)
                    ),
                ),
                "gics_sector": Column(mapper=self.SECTORS_MAP),
                "asset_class": Column(),
                "total_market_value": Column(col_type=ColumnType.NUMERIC),
                "total_notional_value": Column(col_type=ColumnType.NUMERIC),
                "shares_amount": Column(col_type=ColumnType.NUMERIC),
                "share_price": Column(col_type=ColumnType.NUMERIC),
                "country_alpha2": Column(
                    mapper=gen_country_to_alpha_2_map(self.COUNTRY_LANGUAGE)
                ),
                "exchange": Column(),
                "currency": Column(),
            },
            columns_names=self.HOLDINGS_COLUMNS_NAMES,
        )

    def _fetch_raw_listings(self) -> pd.DataFrame:
        return pd.read_json(self.LISTINGS_URL).T

    def _fetch_raw_holdings_by_id(self, product_id: str) -> pd.DataFrame:
        url = self.HOLDINGS_URL_TEMPLATE.format(product_id=product_id)
        df = pd.read_csv(
            url,
            sep=self.HOLDINGS_CSV_SEPARATOR,
            thousands=self.HOLDINGS_CSV_THOUSANDS,
            decimal=self.HOLDINGS_CSV_DECIMAL,
            skiprows=2,
            header=0,
        )
        return df

    def _fetch_raw_holdings_by_isin(self, isin: str) -> pd.DataFrame:
        listings = self.get_listings()
        product_id = listings.loc[isin, "internal_id"]
        return self._fetch_raw_holdings_by_id(product_id)

    def _fetch_raw_holdings_by_ticker(self, ticker: str) -> pd.DataFrame:
        listings = self.get_listings()
        product_id = listings[listings["ticker"] == ticker].iloc[0]["internal_id"]
        return self._fetch_raw_holdings_by_id(product_id)
