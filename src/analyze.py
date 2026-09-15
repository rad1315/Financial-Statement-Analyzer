"""
analyze.py

Command-line entry point:
    python src/analyze.py AAPL

Pulls a company's financial data from SEC EDGAR, calculates ratios for
every fiscal year available, prints the results, and saves them to CSV.
"""

import sys
import os

from edgar_client import EdgarClient
from ratios import build_line_item_table, calculate_ratios


def analyze_ticker(ticker: str):
    print(f"Looking up {ticker} on SEC EDGAR...")
    client = EdgarClient()

    cik = client.get_cik(ticker)
    print(f"  Found CIK: {cik}")

    print("Fetching company facts (this can take a few seconds)...")
    facts = client.get_facts_for_ticker(ticker)

    company_name = facts.get("entityName", ticker)
    print(f"  Company: {company_name}")

    print("Extracting line items and calculating ratios...")
    line_items = build_line_item_table(facts)
    ratios = calculate_ratios(line_items)

    print("\n=== Line items (USD) ===")
    print(line_items.to_string())

    print("\n=== Ratios ===")
    print(ratios.to_string())

    os.makedirs("output", exist_ok=True)
    out_path = f"output/{ticker.upper()}_ratios.csv"
    ratios.to_csv(out_path)
    print(f"\nSaved ratio table to {out_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/analyze.py TICKER")
        print("Example: python src/analyze.py AAPL")
        sys.exit(1)

    ticker = sys.argv[1]
    try:
        analyze_ticker(ticker)
    except Exception as e:
        print(f"\nError: {e}")
        print(
            "\nTip: if this is a KeyError or missing-data issue, the company "
            "may use a different XBRL tag for that line item. Check "
            "src/ratios.py's FALLBACK_TAGS and consider adding the tag you "
            "find in the raw JSON at "
            "https://data.sec.gov/api/xbrl/companyfacts/CIK<10-digit-cik>.json"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
