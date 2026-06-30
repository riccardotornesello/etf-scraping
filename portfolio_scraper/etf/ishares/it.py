from portfolio_scraper.etf.ishares.base import ISharesBaseEtfScraper
from portfolio_scraper.utils.sector import GICSector


class ISharesItScraper(ISharesBaseEtfScraper):
    COUNTRY_LANGUAGE = "it"
    LISTINGS_URL = "https://www.ishares.com/it/investitore-privato/it/product-screener/product-screener-v3.1.jsn?dcrPath=/templatedata/config/product-screener-v3/data/it/it/product-screener/ishares-product-screener-backend-config&siteEntryPassthrough=true"
    HOLDINGS_URL_TEMPLATE = "https://www.ishares.com/it/investitore-privato/it/prodotti/{product_id}/fund/1506575546154.ajax?fileType=csv"

    LISTINGS_COLUMNS_NAMES: dict[str, str] = {
        "internal_id": "portfolioId",
        "name": "fundName",
        "isin": "isin",
        "ticker": "localExchangeTicker",
        "ter": "ter",
    }

    HOLDINGS_COLUMNS_NAMES: dict[str, str] = {
        "name": "Nome",
        "ticker": "Ticker dell'emittente",
        "weight_in_etf": "Ponderazione (%)",
        "gics_sector": "Settore",
        "asset_class": "Asset Class",
        "total_market_value": "Valore di mercato",
        "total_notional_value": "Valore nozionale",
        "shares_amount": "Nominale",
        "share_price": "Prezzo",
        "country_alpha2": "Area Geografica",
        "exchange": "Cambio",
        "currency": "Valuta di mercato",
    }

    SECTORS_MAP: dict[str, GICSector] = {
        "GENERI DI LARGO CONSUMO": GICSector.CONSUMER_DISCRETIONARY,
        "INDUSTRIALI": GICSector.INDUSTRIALS,
        "LIQUIDITÀ E/O DERIVATI": GICSector.UTILITIES,
        "MATERIALI": GICSector.MATERIALS,
        "SALUTE": GICSector.HEALTH_CARE,
    }
