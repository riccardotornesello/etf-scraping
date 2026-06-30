import pandas as pd
import requests

from portfolio_scraper.etf.base import BaseEtfScraper
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


class VanguardGraphQLScraper(BaseEtfScraper):
    GRAPHQL_URL: str
    LISTINGS_PAGE: str

    LISTINGS_COLUMNS_NAMES: dict[str, str] = {
        "internal_id": "portId",
        "name": "fundFullName",
        "isin": "isin",
    }

    HOLDINGS_COLUMNS_NAMES: dict[str, str] = {
        "name": "issuerName",
        "ticker": "ticker",
        "weight_in_etf": "marketValuePercentage",
        "gics_sector": "gicsSectorDescription",
        "asset_class": "securityType",
        "country_alpha2": "bloombergIsoCountry",
    }

    LISTINGS_QUERY = """
        query FundsQuery($portIds: [String!]!) {
            funds(portIds: $portIds) {
                profile {
                    portId
                    polarisPdtTypeIndicator
                    fundIndicator
                    assetClassificationLevel1
                    productTypeLevel1
                    marketOfDomicile
                    consarApproved
                    fundGroupHedgedFunds
                    fundFullName
                    prospectusShareClassName
                    fundInceptionDate
                    currencyHedgingStrategy
                    closedToAllPurchases
                    distributionStrategy
                    fundCurrency
                    investmentStrategy
                    shareClassName
                    managementStrategy
                    marketRegionFocus
                    countryMarketedForSale
                    investmentStrategy
                    identifiers(
                        altIds: ["ISIN", "CITI Code", "CUSIP", "MexId", "Bloomberg", "SEDOL", "WKN Code", "VALOREN - Swiss Security Number", "Ticker", "Bolsa Ticker", "Ticker - Canada", "FundServ Code"]
                    ) {
                        altId
                        altIdCode
                        altIdValue
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
    """

    HOLDINGS_QUERY = """
        query FundsHoldingsQuery($portIds: [String!], $lastItemKey: String) {
            borHoldings(portIds: $portIds) {
                holdings(limit: 1500, lastItemKey: $lastItemKey) {
                items {
                    issuerName
                    securityLongDescription
                    gicsSectorDescription
                    icbSectorDescription
                    icbIndustryDescription
                    marketValuePercentage
                    sedol1
                    quantity
                    ticker
                    securityType
                    finalMaturity
                    effectiveDate
                    marketValueBaseCurrency
                    bloombergIsoCountry
                    couponRate
                    __typename
                }
                totalHoldings
                lastItemKey
                __typename
                }
                __typename
            }
        }
    """

    def __init__(self):
        super().__init__()

        self.LISTINGS_COLUMNS: dict[str, Column] = map_columns(
            columns={
                "internal_id": Column(),
                "name": Column(),
                "isin": Column(),
            },
            columns_names=self.LISTINGS_COLUMNS_NAMES,
        )

        self.HOLDINGS_COLUMNS: dict[str, Column] = map_columns(
            columns={
                "name": Column(),
                "ticker": Column(),
                "weight_in_etf": Column(
                    col_type=ColumnType.NUMERIC,
                    formatter=lambda column: column.div(100),
                ),
                "gics_sector": Column(mapper=SECTORS_MAP),
                "asset_class": Column(),
                "country_alpha2": Column(),
            },
            columns_names=self.HOLDINGS_COLUMNS_NAMES,
        )

    def _fetch_raw_listings(self) -> pd.DataFrame:
        # Extract portIds from listings page HTML
        listings_page_req = requests.get(self.LISTINGS_PAGE)
        listings_page_req.raise_for_status()
        listings_page_html = listings_page_req.text

        port_ids_start_string = '"portIds":"'
        port_ids_start = listings_page_html.find(port_ids_start_string) + len(
            port_ids_start_string
        )
        port_ids_end = listings_page_html.find('"', port_ids_start)
        port_ids = listings_page_html[port_ids_start:port_ids_end].split(",")

        # Make GraphQL request to get listings data
        resp = requests.post(
            self.GRAPHQL_URL,
            headers={"x-consumer-id": "it0"},
            json={
                "operationName": "FundsQuery",
                "variables": {"portIds": port_ids},
                "query": self.LISTINGS_QUERY,
            },
        )
        resp.raise_for_status()

        data = resp.json()
        data = data["data"]["funds"]
        data = [fund["profile"] for fund in data]

        for fund in data:
            identifiers = fund.pop("identifiers")
            for identifier in identifiers:
                if identifier["altId"] == "ISIN":
                    fund["isin"] = identifier["altIdValue"]
                    break

        df = pd.DataFrame(data)
        return df

    def _fetch_raw_holdings_by_id(self, id: str) -> pd.DataFrame:
        df = pd.DataFrame()

        first_request = True
        last_item_key = None
        while first_request or last_item_key is not None:
            first_request = False
            resp = requests.post(
                self.GRAPHQL_URL,
                headers={"x-consumer-id": "it0"},
                json={
                    "operationName": "FundsHoldingsQuery",
                    "variables": {
                        "portIds": [id],
                        "lastItemKey": last_item_key,
                    },
                    "query": self.HOLDINGS_QUERY,
                },
            )
            resp.raise_for_status()

            data = resp.json()
            holdings = data["data"]["borHoldings"][0]["holdings"]["items"]
            last_item_key = data["data"]["borHoldings"][0]["holdings"]["lastItemKey"]
            df = pd.concat([df, pd.DataFrame(holdings)], ignore_index=True)

        return df

    def _fetch_raw_holdings_by_isin(self, isin: str) -> pd.DataFrame:
        listings = self.get_listings()
        product_id = listings.loc[isin, "internal_id"]
        return self._fetch_raw_holdings_by_id(product_id)

    def _fetch_raw_holdings_by_ticker(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError
