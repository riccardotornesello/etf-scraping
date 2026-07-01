import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

from portfolio_scraper.etf import (
    AmundiItScraper,
    ISharesItScraper,
    XtrackersItScraper,
    VanguardItScraper,
)


def alpha2_to_alpha3(code: str) -> str | None:
    """Convert an ISO 3166-1 alpha-2 country code to alpha-3 for the map."""
    try:
        country = pycountry.countries.get(alpha_2=str(code).upper())
        return country.alpha_3 if country else None
    except (KeyError, AttributeError):
        return None


def alpha2_to_name(code: str) -> str:
    """Human-readable country name for an ISO 3166-1 alpha-2 code."""
    try:
        country = pycountry.countries.get(alpha_2=str(code).upper())
        return country.name if country else str(code)
    except (KeyError, AttributeError):
        return str(code)


############################
# LAYOUT
############################
st.set_page_config(
    page_title="Portfolio scraper",
    page_icon="💵",
    layout="wide",
)

############################
# SESSION STATE
############################
if "etfs" not in st.session_state:
    st.session_state.etfs = pd.DataFrame(columns=["ISIN", "Scraper", "Value"])
if "scrapers" not in st.session_state:
    st.session_state.scrapers = {
        "Amundi (IT)": AmundiItScraper(),
        "iShares (IT)": ISharesItScraper(),
        "Vanguard (IT)": VanguardItScraper(),
        "Xtrackers (IT)": XtrackersItScraper(),
    }
if "holdings" not in st.session_state:
    st.session_state.holdings = None


############################
# APP
############################
st.title("💵 Portfolio scraper")
st.caption("Scrape the portfolio of ETFs and analyze its composition.")

st.header("Portfolio")

with st.form("form_add_etf"):
    col1, col2, col3 = st.columns(3)
    isin = col1.text_input("ISIN")
    scraper = col2.selectbox("Scraper", list(st.session_state.scrapers.keys()))
    value = col3.number_input("Value (EUR)", step=0.01)

    add = st.form_submit_button("Add", use_container_width=True)

if add:
    st.session_state.etfs = pd.concat(
        [
            st.session_state.etfs,
            pd.DataFrame({"ISIN": [isin], "Scraper": [scraper], "Value": [value]}),
        ],
        ignore_index=True,
    )
    st.session_state.holdings = None  # reset holdings when a new ETF is added

    st.success(f"Added ETF {isin} with value {value} EUR using scraper {scraper}.")

# Import / export
col_imp, col_exp = st.columns(2)

uploaded = col_imp.file_uploader("Import ETFs (CSV)", type="csv")
if uploaded is not None:
    imported = pd.read_csv(uploaded)
    missing = {"ISIN", "Scraper", "Value"} - set(imported.columns)
    if missing:
        col_imp.error(f"Missing columns in CSV: {', '.join(sorted(missing))}.")
    else:
        st.session_state.etfs = imported[["ISIN", "Scraper", "Value"]].copy()
        st.session_state.holdings = None
        col_imp.success(f"Imported {len(imported)} ETFs.")

col_exp.download_button(
    "Export ETFs (CSV)",
    data=st.session_state.etfs.to_csv(index=False).encode("utf-8"),
    file_name="etfs.csv",
    mime="text/csv",
    use_container_width=True,
    disabled=st.session_state.etfs.empty,
)

# Editable table with row deletion
edited = st.data_editor(
    st.session_state.etfs,
    hide_index=True,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Scraper": st.column_config.SelectboxColumn(
            options=list(st.session_state.scrapers.keys())
        ),
        "Value": st.column_config.NumberColumn(step=0.01),
    },
    key="etf_editor",
)
if not edited.equals(st.session_state.etfs):
    st.session_state.etfs = edited.reset_index(drop=True)
    st.session_state.holdings = None  # reset holdings when the table changes
    st.rerun()


if not st.session_state.etfs.empty:
    st.divider()
    st.header("Scraping")

    scrape = st.button("Scrape ETFs", use_container_width=True)
    if scrape:
        with st.status("Elaboration", expanded=True) as status:
            holdings = []
            for _, row in st.session_state.etfs.iterrows():
                status.update(
                    label=f"Scraping {row['ISIN']} with {row['Scraper']}...",
                    state="running",
                )
                status.text(f"Scraping {row['ISIN']} with {row['Scraper']}...")

                scraper = st.session_state.scrapers[row["Scraper"]]
                etf_holdings = scraper.get_holdings_by_isin(row["ISIN"])
                etf_holdings["etf_value"] = row["Value"]
                etf_holdings["etf_isin"] = row["ISIN"]
                etf_holdings["etf_scraper"] = row["Scraper"]
                holdings.append(etf_holdings)

            holdings_df = pd.concat(holdings, ignore_index=True)
            holdings_df["value_in_portfolio"] = (
                holdings_df["weight_in_etf"].fillna(0) * holdings_df["etf_value"]
            )

            st.session_state.holdings = holdings_df
            status.update(label="Scraping complete!", state="complete", expanded=False)

if st.session_state.holdings is not None:
    st.divider()
    st.header("Analysis")

    # Sidebar filters
    holdings = st.session_state.holdings

    st.sidebar.header("Filters")
    filter_columns = {
        "asset_class": "Asset class",
        "gics_sector": "Sector",
        "country_alpha2": "Country",
        "currency": "Currency",
    }
    for column, label in filter_columns.items():
        if column not in holdings.columns:
            continue
        options = sorted(holdings[column].dropna().unique().tolist())
        if not options:
            continue
        selected = st.sidebar.multiselect(label, options)
        if selected:
            holdings = holdings[holdings[column].isin(selected)]

    if holdings.empty:
        st.warning("No holdings match the current filters.")
        st.stop()

    st.subheader("Composition")

    def composition_pie(column: str, title: str):
        agg = (
            holdings.assign(**{column: holdings[column].fillna("Unknown")})
            .groupby(column, as_index=False)["value_in_portfolio"]
            .sum()
            .sort_values("value_in_portfolio", ascending=False)
        )
        fig = px.pie(
            agg, names=column, values="value_in_portfolio", title=title, hole=0.4
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        return fig

    col1, col2, col3 = st.columns(3)
    col1.plotly_chart(
        composition_pie("country_alpha2", "By country"),
        use_container_width=True,
    )
    col2.plotly_chart(
        composition_pie("gics_sector", "By sector"),
        use_container_width=True,
    )
    col3.plotly_chart(
        composition_pie("asset_class", "By asset class"),
        use_container_width=True,
    )

    st.divider()
    st.subheader("Geographic distribution")

    geo = (
        holdings.dropna(subset=["country_alpha2"])
        .groupby("country_alpha2", as_index=False)["value_in_portfolio"]
        .sum()
    )
    geo["iso_alpha3"] = geo["country_alpha2"].map(alpha2_to_alpha3)
    geo["country"] = geo["country_alpha2"].map(alpha2_to_name)
    geo = geo.dropna(subset=["iso_alpha3"])

    if geo.empty:
        st.info("No country data available for the current holdings.")
    else:
        fig_map = px.choropleth(
            geo,
            locations="iso_alpha3",
            color="value_in_portfolio",
            hover_name="country",
            color_continuous_scale="Blues",
            labels={"value_in_portfolio": "Invested (EUR)"},
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    st.divider()
    st.subheader("Holdings")

    st.dataframe(holdings, hide_index=True)
