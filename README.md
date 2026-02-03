# Financial Forecasting Model

A Python-based financial forecasting tool implementing the **No Plug, No Circularity** methodology by Peraja. This model generates projected Income Statements and Balance Sheets using historical data, ensuring cash is calculated from actual flows rather than forced to balance the sheet.

The repository also includes the original Peraja Excel model as a reference for the Python implementation. We first replicate the Peraja model in Python exactly, then adapt it for real company forecasting.

## Quick Start

```bash
# List available companies
python run.py list

# Run forecast for a company
python run.py forecast ProcterGamble

# Run with full hierarchical output
python run.py forecast ProcterGamble --full

# View company configurations
python run.py config
python run.py config ProcterGamble
```

## Commands

| Command | Description |
|---------|-------------|
| `python run.py forecast <company>` | Run financial forecast |
| `python run.py forecast <company> --full` | Full detailed output |
| `python run.py forecast <company> --base-year 2023` | Override base year |
| `python run.py forecast <company> --years 3` | Override forecast years |
| `python run.py config` | View all company configs |
| `python run.py config <company>` | View specific company config |
| `python run.py list` | List available companies |

## Available Companies

- ProcterGamble (PG)
- CocaCola (KO)
- Costco (COST)
- McDonalds (MCD)

## Project Structure

```
├── run.py                    # Main entry point
├── company_forecast/         # Core forecasting modules
├── configs/                  # Company-specific JSON configurations
├── data/                     # Historical financial data (CSV)
└── example_company_forecast/ # python implementation of example balance sheet model from Pareja 09
```

## Configuration

Each company has a JSON config file in `configs/` with:

- **Forecast Settings**: `base_year`, `n_forecast_years`, `n_input_years`
- **Fixed Assumptions**: `lt_loan_years`, `lt_loan_years`, `pct_financing_with_debt`
- **Optional Overrides**: Override calculated values if needed

Most parameters are automatically calculated from historical data.

## Methodology

This model uses the **No Plug, No Circularity** approach:

1. **Income Statement First**: Revenue → Expenses → Net Income
2. **Cash Budget**: Tracks all cash flows (Operating + Investing + Financing + External + Discretionary)
3. **Debt Schedule**: Manages ST/LT borrowing and repayments
4. **Balance Sheet**: Cash comes from Cash Budget (not forced to balance)
5. **Balance Check**: Verifies Assets = Liabilities + Equity (should be 0)

**Key Difference from "Plug" Method**: Cash is calculated from actual cash flows, not forced to make the balance sheet balance. The model naturally balances if the logic is correct.

## Backtest Mode

If `base_year` is set to a historical year, the model automatically compares forecasted values with actual data.

```bash
# Use 2023 as base year to forecast 2024-2025
python run.py forecast ProcterGamble --base-year 2023
```

## Requirements

- Python 3.8+
- pandas
- numpy
