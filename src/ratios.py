"""
ratios.py

Extracts specific line items from SEC EDGAR "company facts" JSON and
calculates standard financial ratios per fiscal year.

Company facts data is organized as:
  facts["us-gaap"][TAG]["units"]["USD"] = [
      {"end": "2023-09-30", "val": 123456, "fy": 2023, "fp": "FY", "form": "10-K", ...},
      ...
  ]

Different companies sometimes use different XBRL tags for conceptually
the same line item (e.g., "Revenues" vs "RevenueFromContractWithCustomerExcludingAssessedTax").
FALLBACK_TAGS below lists tags to try, in order, for each concept.
"""

import pandas as pd

# For each concept, list possible XBRL tags to try (first match wins per year).
FALLBACK_TAGS = {
    "assets": ["Assets"],
    "current_assets": ["AssetsCurrent"],
    "liabilities": ["Liabilities"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "stockholders_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
    ],
    "net_income": ["NetIncomeLoss"],
}


def _extract_annual_series(facts: dict, tags: list) -> dict:
    """
    Given a list of candidate XBRL tags, return {fiscal_year: value}.

    SEC filings are not perfectly consistent across companies. Some report
    only annual 10-K FY values, while others report only quarterly 10-Q
    data for recent periods. We still want a usable series, so we prefer
    real annual FY rows when available but fall back to any valid yearly
    data point for the same tag if annual entries are missing.
    """
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    annual = {}

    # Walk tags in reverse priority order so earlier tags in the list
    # overwrite later ones when both cover the same fiscal year.
    for tag in reversed(tags):
        if tag not in us_gaap:
            continue

        usd_entries = us_gaap[tag].get("units", {}).get("USD", [])
        for entry in usd_entries:
            fy = entry.get("fy")
            val = entry.get("val")
            if fy is None or val is None:
                continue

            # Prefer true annual FY data when available, but accept other
            # yearly entries (such as quarterly filings with a fiscal year)
            # as a fallback so companies like XOM still produce a series.
            if entry.get("form") == "10-K" and entry.get("fp") == "FY":
                annual[fy] = val
            elif fy not in annual:
                annual[fy] = val

    return annual


def build_line_item_table(facts: dict) -> pd.DataFrame:
    """
    Build a DataFrame indexed by fiscal year with one column per line item
    concept (assets, revenue, net_income, etc.).
    """
    data = {}
    for concept, tags in FALLBACK_TAGS.items():
        data[concept] = _extract_annual_series(facts, tags)

    df = pd.DataFrame(data)
    df.index.name = "fiscal_year"
    df = df.sort_index()
    return df


def calculate_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a line-item DataFrame (see build_line_item_table), calculate
    standard ratios for each fiscal year. Missing inputs produce NaN
    rather than raising an error, so partial data still returns a result.
    """
    ratios = pd.DataFrame(index=df.index)

    ratios["current_ratio"] = df["current_assets"] / df["current_liabilities"]
    ratios["net_profit_margin"] = df["net_income"] / df["revenue"]
    ratios["return_on_assets"] = df["net_income"] / df["assets"]
    ratios["return_on_equity"] = df["net_income"] / df["stockholders_equity"]
    ratios["debt_to_equity"] = df["liabilities"] / df["stockholders_equity"]
    ratios["asset_turnover"] = df["revenue"] / df["assets"]

    return ratios.round(3)
