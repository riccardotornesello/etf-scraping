import pandas as pd
import requests

from portfolio_scraper.etf.base import BaseEtfScraper
from portfolio_scraper.utils.country import gen_country_to_alpha_2_map
from portfolio_scraper.utils.dataframe import Column, ColumnType, map_columns
from portfolio_scraper.utils.sector import GICSector


SECTORS_MAP: dict[str, GICSector] = {
    "COMMUNICATION SERVICES": GICSector.COMMUNICATION_SERVICES,
    "CONSUMER DISCRETIONARY": GICSector.CONSUMER_DISCRETIONARY,
    "CONSUMER STAPLES": GICSector.CONSUMER_STAPLES,
    "ENERGY": GICSector.ENERGY,
    "FINANCIALS": GICSector.FINANCIALS,
    "HEALTH CARE": GICSector.HEALTH_CARE,
    "INDUSTRIALS": GICSector.INDUSTRIALS,
    "INFORMATION TECHNOLOGY": GICSector.INFORMATION_TECHNOLOGY,
    "MATERIALS": GICSector.MATERIALS,
    "REAL ESTATE": GICSector.REAL_ESTATE,
    "UTILITIES": GICSector.UTILITIES,
}


class AmundiBaseEtfScraper(BaseEtfScraper):
    COUNTRY_LANGUAGE: str
    HOLDINGS_URL: str
    HOLDINGS_COLUMNS_NAMES: dict[str, str]

    def __init__(self):
        super().__init__()

        self.HOLDINGS_COLUMNS: dict[str, Column] = map_columns(
            columns={
                "name": Column(),
                "isin": Column(),
                "weight_in_etf": Column(col_type=ColumnType.NUMERIC),
                "gics_sector": Column(mapper=SECTORS_MAP),
                "asset_class": Column(),
                "shares_amount": Column(col_type=ColumnType.NUMERIC),
                "country_alpha2": Column(
                    mapper=gen_country_to_alpha_2_map(self.COUNTRY_LANGUAGE)
                ),
                "currency": Column(),
            },
            columns_names=self.HOLDINGS_COLUMNS_NAMES,
        )

    def _fetch_raw_listings(self) -> pd.DataFrame:
        raise NotImplementedError

    def _fetch_raw_holdings_by_id(self, isin: str) -> pd.DataFrame:
        return self._fetch_raw_holdings_by_isin(isin)

    def _fetch_raw_holdings_by_isin(self, isin: str) -> pd.DataFrame:
        url = self.HOLDINGS_URL
        payload = {
            "composition": {
                "compositionFields": [
                    "date",
                    "type",
                    "bbg",
                    "isin",
                    "name",
                    "weight",
                    "quantity",
                    "currency",
                    "sector",
                    "country",
                    "countryOfRisk",
                ]
            },
            "productIds": [isin],
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = [
            element["compositionCharacteristics"]
            for element in response.json()["products"][0]["composition"][
                "compositionData"
            ]
        ]
        df = pd.DataFrame(data)
        return df

    def _fetch_raw_holdings_by_ticker(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError(
            "Amundi Italy ETF holdings by ticker is not implemented yet."
        )
