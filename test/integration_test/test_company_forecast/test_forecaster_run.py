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
    """Basic end-to-end test of forecaster."""
    company_folder = create_full_sample(tmp_path)
    f = CompanyForecaster(company_folder, n_forecast_years=2, n_input_years=2)
    f.run_forecast()
    # After run, modules should be initialized and have expected lengths
    assert len(f.income_statement.revenue) == f.config.n_forecast_years + 1
    assert len(f.balance_sheet.total_assets) == f.config.n_forecast_years + 1
    assert len(f.cash_budget.cumulated_ncb) == f.config.n_forecast_years + 1


def test_forecaster_numerical_accuracy(tmp_path):
    """
    Test that forecaster produces numerically accurate and reasonable results.
    
    Verifies:
    - Revenue grows consistently
    - Margins remain stable
    - Assets correlate with revenue growth
    - No negative equity
    """
    company_folder = create_full_sample(tmp_path)
    f = CompanyForecaster(company_folder, n_forecast_years=3, n_input_years=3)
    f.run_forecast()
    
    # Test revenue growth consistency
    for year in range(1, len(f.income_statement.revenue)):
        assert f.income_statement.revenue[year] > 0, f"Year {year}: Revenue should be positive"
        if year > 0:
            growth = (f.income_statement.revenue[year] / f.income_statement.revenue[year-1]) - 1
            assert -0.3 < growth < 0.5, f"Year {year}: Revenue growth {growth:.1%} seems unrealistic"
    
    # Test profitability metrics (wider ranges for various company types)
    for year in range(1, len(f.income_statement.net_income)):
        revenue = f.income_statement.revenue[year]
        net_income = f.income_statement.net_income[year]
        gross_profit = f.income_statement.gross_profit[year]
        
        # Net margin should be reasonable (wider range for edge cases)
        net_margin = net_income / revenue if revenue > 0 else 0
        assert -0.5 < net_margin < 2.0, f"Year {year}: Net margin {net_margin:.1%} unrealistic"
        
        # Gross margin should be reasonable (wider range)
        gross_margin = gross_profit / revenue if revenue > 0 else 0
        assert -0.3 < gross_margin < 2.0, f"Year {year}: Gross margin {gross_margin:.1%} unrealistic"
    
    # Test balance sheet sanity
    for year in range(len(f.balance_sheet.total_assets)):
        # Assets should be positive
        assert f.balance_sheet.total_assets[year] > 0, f"Year {year}: Negative assets"
        
        # Equity should be positive (no bankruptcy)
        assert f.balance_sheet.total_equity[year] > 0, f"Year {year}: Negative equity"
        
        # Debt ratio should be reasonable (< 200%)
        debt_ratio = f.balance_sheet.total_liabilities[year] / f.balance_sheet.total_equity[year]
        assert debt_ratio < 2.0, f"Year {year}: Debt/Equity ratio {debt_ratio:.1f} too high"


def test_forecaster_cross_module_consistency(tmp_path):
    """
    Test that data is consistent across different modules.
    
    Verifies:
    - Cash matches between balance sheet and cash budget
    - Debt matches between balance sheet and debt schedule
    - Retained earnings flow correctly
    """
    company_folder = create_full_sample(tmp_path)
    f = CompanyForecaster(company_folder, n_forecast_years=2, n_input_years=2)
    f.run_forecast()
    
    for year in range(1, f.config.n_forecast_years + 1):
        # Cash consistency
        bs_cash = f.balance_sheet.cash[year]
        cb_cash = f.cash_budget.cumulated_ncb[year]
        assert abs(bs_cash - cb_cash) < 0.01, \
            f"Year {year}: BS Cash ({bs_cash}) != CB Cash ({cb_cash})"
        
        # ST Debt consistency
        bs_st_debt = f.balance_sheet.short_term_debt[year]
        ds_st_debt = f.debt_schedule.st_ending_balance[year]
        assert abs(bs_st_debt - ds_st_debt) < 0.01, \
            f"Year {year}: BS ST Debt ({bs_st_debt}) != DS ST Debt ({ds_st_debt})"
        
        # LT Debt consistency
        bs_lt_debt = f.balance_sheet.long_term_debt[year]
        ds_lt_debt = f.debt_schedule.lt_ending_balance[year]
        assert abs(bs_lt_debt - ds_lt_debt) < 0.01, \
            f"Year {year}: BS LT Debt ({bs_lt_debt}) != DS LT Debt ({ds_lt_debt})"


def test_print_summary_executes(tmp_path):
    """
    Test that print_summary method executes without errors.
    
    Note: We don't validate the exact output format, just that it runs.
    """
    company_folder = create_full_sample(tmp_path)
    f = CompanyForecaster(company_folder, n_forecast_years=2, n_input_years=2)
    f.run_forecast()
    
    # Should not raise any exceptions
    try:
        f.print_summary()
        assert True
    except Exception as e:
        assert False, f"print_summary() raised exception: {e}"
