from portfolio_scraper.etf.amundi.base import AmundiBaseEtfScraper


class AmundiItScraper(AmundiBaseEtfScraper):
    COUNTRY_LANGUAGE = "en"
    HOLDINGS_URL = "https://www.amundietf.it/mapi/ProductAPI/getProductsData"

    HOLDINGS_COLUMNS_NAMES = {
        "name": "name",
        "isin": "isin",
        "weight_in_etf": "weight",
        "gics_sector": "sector",
        "asset_class": "type",
        "shares_amount": "quantity",
        "country_alpha2": "countryOfRisk",
        "currency": "currency",
    }
