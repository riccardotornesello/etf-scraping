from abc import ABC, abstractmethod

import pandas as pd

from portfolio_scraper.utils.dataframe import (
    prepare_dataframe,
    Column,
    ColumnType,
)


LISTINGS_COLUMNS: dict[str, Column] = {
    "internal_id": Column(),  # Unique identifier for the ETF in the scraper's database
    "name": Column(),
    "isin": Column(),
    "ticker": Column(),
    "ter": Column(col_type=ColumnType.NUMERIC),  # Total Expense Ratio as a decimal
    "profit_distribution_strategy": Column(),  # TODO: enum
}

ALLOWED_HOLDINGS_COLUMNS: list[str] = [
    # Basic information
    "name",
    "isin",
    "ticker",
    # ETF-specific information
    "weight_in_etf",
    # Generic holding information
    "gics_sector",
    "rating",
    "asset_class",
    "total_market_value",
    "total_notional_value",
    "shares_amount",
    "share_price",
    "country_alpha2",
    "exchange",
    "currency",
]


class BaseEtfScraper(ABC):
    """
    Base class for ETF scrapers. Provides methods to fetch listings and holdings data.
    """

    LISTINGS_COLUMNS: dict[str, Column] = {}
    HOLDINGS_COLUMNS: dict[str, Column] = {}

    listings_cache: pd.DataFrame | None = None

    def get_listings(self, refresh: bool = False) -> pd.DataFrame:
        """
        Get the ETF listings. Caches the result to avoid redundant fetching.
        """
        if self.listings_cache is None or refresh:
            self.listings_cache = self.fetch_listings()
        return self.listings_cache

    def fetch_listings(self) -> pd.DataFrame:
        """
        Fetch the ETF listings from the source. Must be implemented by subclasses.
        """
        df = self._fetch_raw_listings()
        df = self._prepare_listings(df)
        df = prepare_dataframe(df, LISTINGS_COLUMNS, index_col="isin")
        return df

    def get_holdings_by_id(self, internal_id: str) -> pd.DataFrame:
        """
        Get the holdings of an ETF by its internal ID.
        """
        df = self._fetch_raw_holdings_by_id(internal_id)
        df = self._prepare_holdings(df)
        return df

    def get_holdings_by_isin(self, isin: str) -> pd.DataFrame:
        """
        Get the holdings of an ETF by its ISIN.
        """
        df = self._fetch_raw_holdings_by_isin(isin)
        df = self._prepare_holdings(df)
        return df

    def get_holdings_by_ticker(self, ticker: str) -> pd.DataFrame:
        """
        Get the holdings of an ETF by its ticker.
        """
        df = self._fetch_raw_holdings_by_ticker(ticker)
        df = self._prepare_holdings(df)
        return df

    @abstractmethod
    def _fetch_raw_listings(self) -> pd.DataFrame:
        """
        Fetch the raw ETF listings from the source. Must be implemented by subclasses.
        It returns a DataFrame with the raw data, without mapping and with more columns than the final output.
        """
        raise NotImplementedError

    def _prepare_listings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename the columns and update the output.
        Can be overridden by subclasses for custom processing.
        """
        df = prepare_dataframe(df, self.LISTINGS_COLUMNS)
        return df

    @abstractmethod
    def _fetch_raw_holdings_by_id(self, product_id: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def _fetch_raw_holdings_by_isin(self, isin: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def _fetch_raw_holdings_by_ticker(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError

    def _prepare_holdings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename the columns and update the output.
        Can be overridden by subclasses for custom processing.
        """
        df = prepare_dataframe(
            df,
            self.HOLDINGS_COLUMNS,
            all_columns=ALLOWED_HOLDINGS_COLUMNS,
        )
        return df
