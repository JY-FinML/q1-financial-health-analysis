import os
import pandas as pd
from company_forecast.forecaster import CompanyForecaster


def create_full_sample(tmp_path):
    folder = tmp_path / "TestCo"
    folder.mkdir()
    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]

    income_index = [
        'Total Revenue', 'Cost Of Revenue', 'Gross Profit', 'Operating Income',
        'Selling General And Administration', 'Reconciled Depreciation',
        'Interest Expense', 'Pretax Income', 'Tax Provision', 'Net Income', 'Interest Income'
    ]

    income = pd.DataFrame({
        cols[0]: [120, -72, 48, 30, -12, -5, -1, 24, -4, 20, 0],
        cols[1]: [110, -66, 44, 28, -11, -5, -1, 22, -4, 18, 0],
        cols[2]: [100, -60, 40, 26, -10, -5, -1, 20, -4, 16, 0],
    }, index=income_index)

    balance_index = [
        'Total Assets', 'Accounts Receivable', 'Inventory', 'Current Assets',
        'Net PPE', 'Gross PPE', 'Accumulated Depreciation', 'Total Liabilities Net Minority Interest',
        'Current Liabilities', 'Current Debt', 'Long Term Debt', 'Stockholders Equity', 'Retained Earnings', 'Minority Interest', 'Cash And Cash Equivalents'
    ]

    balance = pd.DataFrame({
        cols[0]: [500, 20, 10, 100, 200, 250, -30, 300, 80, 10, 150, 200, 50, 0, 5],
        cols[1]: [480, 18, 9, 96, 190, 240, -30, 290, 78, 9, 140, 200, 48, 0, 4],
        cols[2]: [460, 16, 8, 92, 180, 230, -30, 280, 76, 8, 130, 200, 46, 0, 3],
    }, index=balance_index)

    cash_index = ['Operating Cash Flow', 'Capital Expenditure', 'Cash Dividends Paid', 'Common Stock Payments']
    cash = pd.DataFrame({
        cols[0]: [30, -5, -2, -1],
        cols[1]: [28, -5, -2, -1],
        cols[2]: [26, -5, -2, -1],
    }, index=cash_index)

    income.to_csv(folder / "income statement.csv")
    balance.to_csv(folder / "balance sheet.csv")
    cash.to_csv(folder / "cash flow.csv")

    return str(folder)


def test_forecaster_end_to_end(tmp_path):
    company_folder = create_full_sample(tmp_path)
    f = CompanyForecaster(company_folder, n_forecast_years=2, n_input_years=2)
    f.run_forecast()
    # After run, modules should be initialized and have expected lengths
    assert len(f.income_statement.revenue) == f.config.n_forecast_years + 1
    assert len(f.balance_sheet.total_assets) == f.config.n_forecast_years + 1
    assert len(f.cash_budget.cumulated_ncb) == f.config.n_forecast_years + 1
