"""
edgar_client.py

Thin client for pulling data from SEC EDGAR's public APIs:
  - Ticker -> CIK lookup
  - Company Facts (structured XBRL data) by CIK

SEC EDGAR API docs: https://www.sec.gov/edgar/sec-api-documentation

IMPORTANT: SEC requires all automated requests to include a descriptive
User-Agent header (your name + email). Requests without one may be
blocked. Replace the placeholder below before running this project.
"""

import requests

USER_AGENT = "Richard Daley richarddaleyii@gmail.com"  # <-- REPLACE THIS

HEADERS = {"User-Agent": USER_AGENT}

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"


class EdgarClient:
    def __init__(self):
        self._ticker_to_cik = None  # cached lookup table

    def _load_ticker_map(self):
        """Fetch and cache SEC's full ticker -> CIK mapping."""
        if self._ticker_to_cik is not None:
            return

        resp = requests.get(TICKER_MAP_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        raw = resp.json()

        # raw is a dict of dicts like {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
        self._ticker_to_cik = {
            entry["ticker"].upper(): entry["cik_str"] for entry in raw.values()
        }

    def get_cik(self, ticker: str) -> int:
        """Look up a company's CIK (SEC's internal ID) from its ticker symbol."""
        self._load_ticker_map()
        ticker = ticker.upper().strip()

        if ticker not in self._ticker_to_cik:
            raise ValueError(
                f"Ticker '{ticker}' not found in SEC's ticker list. "
                "Double check the symbol, or the company may not file with the SEC."
            )
        return self._ticker_to_cik[ticker]

    def get_company_facts(self, cik: int) -> dict:
        """
        Fetch the full company facts payload (all XBRL data the company
        has ever reported) for a given CIK.
        """
        url = COMPANY_FACTS_URL.format(cik=cik)
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_facts_for_ticker(self, ticker: str) -> dict:
        """Convenience method: ticker -> full company facts JSON."""
        cik = self.get_cik(ticker)
        return self.get_company_facts(cik)
