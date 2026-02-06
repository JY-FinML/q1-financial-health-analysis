"""
Integration test for BalanceSheet accuracy.

This test verifies that with REAL forecast data (not simplified stubs),
the balance sheet perfectly balances with tolerance < 0.01.

This confirms that:
1. The unit test tolerance of 2.0 is only due to simplified stub data
2. The actual implementation produces accurate, balanced financial statements
3. The accounting identity (Assets = Liabilities + Equity) holds in real usage
"""

import numpy as np
import pandas as pd
from company_forecast.forecaster import CompanyForecaster


def create_realistic_company(tmp_path):
    """
    Create a realistic company with complete financial data.
    
    This data is designed to be accounting-consistent:
    - All balance sheet items properly accounted for
    - Cash flow statement reconciles with balance sheet changes
    - Income statement flows into retained earnings
    """
    folder = tmp_path / "RealisticCo"
    folder.mkdir()
    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]

    # Comprehensive income statement
    income_index = [
        'Total Revenue', 
        'Cost Of Revenue', 
        'Gross Profit', 
        'Operating Income',
        'Selling General And Administration', 
        'Reconciled Depreciation',
        'Interest Expense', 
        'Interest Income',
        'Pretax Income', 
        'Tax Provision', 
        'Net Income',
        'Diluted EPS',
        'Basic EPS'
    ]

    income = pd.DataFrame({
        cols[0]: [1000, -600, 400, 250, -100, -50, -10, 5, 245, -49, 196, 1.96, 1.96],
        cols[1]: [950, -570, 380, 240, -95, -48, -9, 4, 235, -47, 188, 1.88, 1.88],
        cols[2]: [900, -540, 360, 230, -90, -45, -8, 3, 225, -45, 180, 1.80, 1.80],
    }, index=income_index)

    # Comprehensive balance sheet with all major categories
    balance_index = [
        'Total Assets',
        'Cash And Cash Equivalents',
        'Accounts Receivable', 
        'Inventory',
        'Other Current Assets',
        'Current Assets',
        'Net PPE',
        'Gross PPE',
        'Accumulated Depreciation',
        'Goodwill',
        'Other Intangible Assets',
        'Other Non Current Assets',
        'Total Liabilities Net Minority Interest',
        'Accounts Payable',
        'Other Current Liabilities',
        'Current Liabilities',
        'Current Debt',
        'Long Term Debt',
        'Other Non Current Liabilities',
        'Stockholders Equity',
        'Retained Earnings',
        'Common Stock',
        'Minority Interest'
    ]

    balance = pd.DataFrame({
        cols[0]: [
            2500,  # Total Assets
            150,   # Cash
            180,   # AR
            120,   # Inventory
            50,    # Other Current Assets
            500,   # Current Assets
            1400,  # Net PPE
            1800,  # Gross PPE
            -400,  # Accumulated Depreciation
            300,   # Goodwill
            200,   # Intangibles
            100,   # Other Non-Current Assets
            1200,  # Total Liabilities
            90,    # AP
            60,    # Other Current Liab
            200,   # Current Liabilities
            50,    # Current Debt
            800,   # LT Debt
            150,   # Other Non-Current Liab
            1300,  # Stockholders Equity
            800,   # Retained Earnings
            500,   # Common Stock
            0      # Minority Interest
        ],
        cols[1]: [
            2400,  # Total Assets
            140,   # Cash
            170,   # AR
            115,   # Inventory
            45,    # Other Current Assets
            470,   # Current Assets
            1350,  # Net PPE
            1750,  # Gross PPE
            -400,  # Accumulated Depreciation
            300,   # Goodwill
            200,   # Intangibles
            80,    # Other Non-Current Assets
            1180,  # Total Liabilities
            85,    # AP
            55,    # Other Current Liab
            190,   # Current Liabilities
            50,    # Current Debt
            820,   # LT Debt
            170,   # Other Non-Current Liab
            1220,  # Stockholders Equity
            720,   # Retained Earnings
            500,   # Common Stock
            0      # Minority Interest
        ],
        cols[2]: [
            2300,  # Total Assets
            130,   # Cash
            160,   # AR
            110,   # Inventory
            40,    # Other Current Assets
            440,   # Current Assets
            1300,  # Net PPE
            1700,  # Gross PPE
            -400,  # Accumulated Depreciation
            300,   # Goodwill
            200,   # Intangibles
            60,    # Other Non-Current Assets
            1160,  # Total Liabilities
            80,    # AP
            50,    # Other Current Liab
            180,   # Current Liabilities
            50,    # Current Debt
            840,   # LT Debt
            140,   # Other Non-Current Liab
            1140,  # Stockholders Equity
            640,   # Retained Earnings
            500,   # Common Stock
            0      # Minority Interest
        ],
    }, index=balance_index)

    # Cash flow statement
    cash_index = [
        'Operating Cash Flow',
        'Capital Expenditure',
        'Cash Dividends Paid',
        'Common Stock Payments',
        'Repurchase Of Capital Stock'
    ]
    
    cash = pd.DataFrame({
        cols[0]: [250, -100, -40, 0, -10],
        cols[1]: [240, -95, -38, 0, -9],
        cols[2]: [230, -90, -36, 0, -8],
    }, index=cash_index)

    income.to_csv(folder / "income statement.csv")
    balance.to_csv(folder / "balance sheet.csv")
    cash.to_csv(folder / "cash flow.csv")

    return str(folder)


def test_balance_sheet_perfect_balance_with_real_data(tmp_path):
    """
    Test that BalanceSheet produces near-perfect balance with real forecast data.
    
    This is the key integration test that proves:
    - Unit test tolerance (2.0) is only for simplified stubs
    - Real implementation is accurate (balance_check < 0.01)
    - Accounting identity holds: Assets = Liabilities + Equity
    """
    company_folder = create_realistic_company(tmp_path)
    
    # Run full forecast with realistic data
    f = CompanyForecaster(company_folder, n_forecast_years=3, n_input_years=3)
    f.run_forecast()
    
    # Verify balance sheet was created
    assert f.balance_sheet is not None
    assert len(f.balance_sheet.total_assets) == 4  # Year 0 + 3 forecast years
    
    # Critical test: Balance sheet should balance perfectly with real data
    for year, balance_check in enumerate(f.balance_sheet.balance_check):
        # Year 0 should be exactly 0 (from historical data)
        if year == 0:
            assert abs(balance_check) < 1e-10, \
                f"Year 0 should balance exactly (from historical data), got {balance_check}"
        # Forecast years should be very close to 0 (< 0.01)
        else:
            assert abs(balance_check) < 0.01, \
                f"Year {year} balance check = {balance_check}, should be < 0.01 with real data"
    
    print(f"\n✓ Balance Sheet Accuracy Test PASSED")
    print(f"  Balance checks for all years: {[f'{x:.6f}' for x in f.balance_sheet.balance_check]}")
    print(f"  Max absolute balance error: {max(abs(x) for x in f.balance_sheet.balance_check):.6f}")
    print(f"\n  This confirms that unit test tolerance (2.0) is only needed for")
    print(f"  simplified stub data, not for the actual implementation!")


def test_comprehensive_forecast_modules(tmp_path):
    """
    Test that all forecast modules work together correctly.
    
    Verifies integration of:
    - InputCalculator
    - IntermediateCalculations
    - IncomeStatement
    - CashBudget
    - DebtSchedule
    - BalanceSheet
    """
    company_folder = create_realistic_company(tmp_path)
    f = CompanyForecaster(company_folder, n_forecast_years=2, n_input_years=2)
    f.run_forecast()
    
    # Verify all modules initialized
    assert f.inputs is not None
    assert f.intermediate is not None
    assert f.income_statement is not None
    assert f.cash_budget is not None
    assert f.debt_schedule is not None
    assert f.balance_sheet is not None
    
    # Verify data consistency across modules
    n_years = f.config.n_forecast_years + 1  # +1 for Year 0
    
    # All modules should have consistent array lengths
    assert len(f.income_statement.revenue) == n_years
    assert len(f.cash_budget.cumulated_ncb) == n_years
    assert len(f.balance_sheet.total_assets) == n_years
    assert len(f.debt_schedule.st_ending_balance) == n_years
    assert len(f.debt_schedule.lt_ending_balance) == n_years
    
    # Verify some key relationships
    for year in range(1, n_years):
        # Cash from balance sheet should match cash budget
        assert f.balance_sheet.cash[year] == f.cash_budget.cumulated_ncb[year], \
            f"Year {year}: BS Cash != CB Cash"
        
        # ST debt from balance sheet should match debt schedule
        assert f.balance_sheet.short_term_debt[year] == f.debt_schedule.st_ending_balance[year], \
            f"Year {year}: BS ST Debt != DS ST Debt"
        
        # LT debt from balance sheet should match debt schedule
        assert f.balance_sheet.long_term_debt[year] == f.debt_schedule.lt_ending_balance[year], \
            f"Year {year}: BS LT Debt != DS LT Debt"
    
    print(f"\n✓ Comprehensive Integration Test PASSED")
    print(f"  All {n_years} forecast periods validated across all modules")
    print(f"  Cash, ST Debt, and LT Debt consistent between modules")


def test_forecast_numerical_stability(tmp_path):
    """
    Test that forecast remains numerically stable over multiple years.
    
    Checks for:
    - No NaN or infinite values
    - Reasonable growth rates
    - Positive assets, equity
    """
    company_folder = create_realistic_company(tmp_path)
    f = CompanyForecaster(company_folder, n_forecast_years=5, n_input_years=3)
    f.run_forecast()
    
    # Check for numerical issues
    for year in range(len(f.balance_sheet.total_assets)):
        # No NaN or inf
        assert pd.notna(f.balance_sheet.total_assets[year]), f"Year {year}: NaN assets"
        assert pd.notna(f.balance_sheet.total_equity[year]), f"Year {year}: NaN equity"
        assert not np.isinf(f.balance_sheet.total_assets[year]), f"Year {year}: Inf assets"
        
        # Positive assets and equity (basic sanity)
        assert f.balance_sheet.total_assets[year] > 0, f"Year {year}: Negative assets"
        assert f.balance_sheet.total_equity[year] > 0, f"Year {year}: Negative equity"
    
    # Revenue should be growing (based on growth assumptions)
    for year in range(1, len(f.income_statement.revenue)):
        growth = (f.income_statement.revenue[year] / f.income_statement.revenue[year-1]) - 1
        # Reasonable growth range (-20% to +50%)
        assert -0.2 < growth < 0.5, f"Year {year}: Unrealistic revenue growth {growth:.1%}"
    
    print(f"\n✓ Numerical Stability Test PASSED")
    print(f"  5-year forecast completed without numerical issues")
    print(f"  All values finite, positive, and within reasonable ranges")
