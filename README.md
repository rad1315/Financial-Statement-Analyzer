# Financial Statement Analyzer

A tool that pulls real company filings from the SEC's EDGAR database and
calculates liquidity, profitability, leverage, and efficiency ratios —
turning raw financial statement data into an actual analysis.

## Why this project

Public companies are required to file structured, machine-readable
financial data (XBRL) with the SEC. This project uses SEC EDGAR's free,
public API to pull that data directly — no manual copy-pasting from PDFs —
and turns it into ratio analysis you'd see in a real equity research note
or credit memo.

## Project roadmap

- **Phase 1 (start here):** Pull one company's data, calculate core ratios
  across multiple fiscal years, print/save a clean table.
- **Phase 2:** Compare 4–5 companies in the same industry.
- **Phase 3:** Add a company from a different industry, compare capital
  structure and margin differences.
- **Phase 4:** Add "earnings quality" flags (e.g., net income vs. operating
  cash flow divergence, unusual accrual growth).
- **Phase 5:** Wrap it in a simple Streamlit dashboard.

This repo currently implements **Phase 1**.

## Setup

1. Clone/open this folder in VS Code.
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Important — SEC requires a User-Agent header identifying you.**
   Open `src/edgar_client.py` and replace the placeholder in `USER_AGENT`
   with your own name and email, e.g.:
   ```python
   USER_AGENT = "Jane Doe janedoe@email.com"
   ```
   Requests without a proper User-Agent will be blocked or rate-limited.

## Usage

Run the analyzer for a single company by ticker:

```bash
python src/analyze.py AAPL
```

This will:
1. Look up the company's CIK (SEC's internal ID) from its ticker.
2. Pull its structured financial facts (XBRL) from EDGAR.
3. Calculate key ratios for each fiscal year available.
4. Print a table to the console and save it to `output/AAPL_ratios.csv`.

## Ratios calculated (Phase 1)

| Category      | Ratio                        | Formula                                  |
|----------------|-------------------------------|-------------------------------------------|
| Liquidity      | Current Ratio                 | Current Assets / Current Liabilities      |
| Profitability  | Net Profit Margin              | Net Income / Revenue                      |
| Profitability  | Return on Assets (ROA)         | Net Income / Total Assets                 |
| Profitability  | Return on Equity (ROE)         | Net Income / Stockholders' Equity         |
| Leverage       | Debt-to-Equity                 | Total Liabilities / Stockholders' Equity  |
| Efficiency     | Asset Turnover                 | Revenue / Total Assets                    |

## Notes on data quality

Not every company tags every line item the same way in XBRL (e.g., some
use `Liabilities`, others break it into current/non-current only). The
code includes fallback logic for the most common tag variations, but if
you hit a `KeyError` or missing value for a specific company, that's a
great opportunity to inspect the raw JSON (`data.sec.gov/api/xbrl/companyfacts/`)
and extend the mapping — this is a realistic part of working with real
filings, not a bug in the sense of "something's wrong with your code."

## A note for your write-up / resume

Keep a short analysis memo (even just `analysis/aapl_memo.md`) alongside
the code — 2-3 paragraphs interpreting what the ratios actually mean for
the company's financial health. That's the piece that makes this an
*accounting* project instead of a coding exercise.
