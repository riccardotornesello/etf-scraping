import pandas as pd

from scrapers.base import BaseScraper
from utils.dataframe import Column, rename_dataframe_columns


class ISharesBaseScraper(BaseScraper):
    LISTINGS_URL: str
    LISTINGS_COLUMN_NAMES: dict[str, Column]
    HOLDINGS_URL_TEMPLATE: str
    HOLDINGS_COLUMN_NAMES: dict[str, str]
    HOLDINGS_CSV_SEPARATOR: str
    HOLDINGS_CSV_THOUSANDS: str
    HOLDINGS_CSV_DECIMAL: str

    def _fetch_listings(self) -> pd.DataFrame:
        return rename_dataframe_columns(
            pd.read_json(self.LISTINGS_URL).T,
            self.LISTINGS_COLUMN_NAMES,
        )

    def _get_holdings_by_id(self, product_id: str) -> pd.DataFrame:
        url = self.HOLDINGS_URL_TEMPLATE.format(product_id=product_id)
        df = pd.read_csv(
            url,
            sep=self.HOLDINGS_CSV_SEPARATOR,
            thousands=self.HOLDINGS_CSV_THOUSANDS,
            decimal=self.HOLDINGS_CSV_DECIMAL,
            skiprows=2,
            header=0,
        )
        df = rename_dataframe_columns(df, self.HOLDINGS_COLUMN_NAMES)
        df["weight_in_etf"] = df["weight_in_etf"] / 100
        return df

    def _get_holdings_by_isin(self, isin: str) -> pd.DataFrame:
        listings = self.get_listings()
        product_id = listings.loc[isin, "internal_id"]
        return self._get_holdings_by_id(product_id)

    def _get_holdings_by_ticker(self, ticker: str) -> pd.DataFrame:
        listings = self.get_listings()
        product_id = listings[listings["ticker"] == ticker].iloc[0]["internal_id"]
        return self._get_holdings_by_id(product_id)
