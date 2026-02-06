"""
Shared test fixtures and utilities for all tests.
This file provides common test data and helper functions.
"""

import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_financial_data():
    """
    Returns a dictionary with sample financial data for testing.
    This represents a simplified but realistic company financial structure.
    """
    return {
        'columns': ["2023-12-31", "2022-12-31", "2021-12-31"],
        'income_statement': {
            'Total Revenue': [120.0, 110.0, 100.0],
            'Cost Of Revenue': [-72.0, -66.0, -60.0],
            'Gross Profit': [48.0, 44.0, 40.0],
            'Operating Expense': [-18.0, -16.0, -14.0],
            'Selling General And Administration': [-12.0, -11.0, -10.0],
            'Reconciled Depreciation': [-5.0, -5.0, -5.0],
            'Operating Income': [30.0, 28.0, 26.0],
            'EBIT': [30.0, 28.0, 26.0],
            'Interest Expense': [-2.0, -2.0, -2.0],
            'Interest Income': [0.5, 0.4, 0.3],
            'Pretax Income': [28.5, 26.4, 24.3],
            'Tax Provision': [-5.7, -5.28, -4.86],
            'Net Income': [22.8, 21.12, 19.44],
        },
        'balance_sheet': {
            'Cash And Cash Equivalents': [15.0, 12.0, 10.0],
            'Cash Cash Equivalents And Short Term Investments': [15.0, 12.0, 10.0],
            'Accounts Receivable': [10.0, 9.0, 8.0],
            'Inventory': [8.0, 7.0, 6.0],
            'Current Assets': [40.0, 35.0, 30.0],
            'Gross PPE': [250.0, 240.0, 230.0],
            'Accumulated Depreciation': [-50.0, -45.0, -40.0],
            'Net PPE': [200.0, 195.0, 190.0],
            'Goodwill': [20.0, 20.0, 20.0],
            'Other Intangible Assets': [10.0, 10.0, 10.0],
            'Total Assets': [300.0, 290.0, 280.0],
            'Accounts Payable': [5.0, 4.5, 4.0],
            'Current Debt': [10.0, 9.0, 8.0],
            'Current Liabilities': [30.0, 28.0, 26.0],
            'Long Term Debt': [100.0, 95.0, 90.0],
            'Total Liabilities Net Minority Interest': [150.0, 145.0, 140.0],
            'Stockholders Equity': [150.0, 145.0, 140.0],
            'Retained Earnings': [80.0, 70.0, 60.0],
            'Minority Interest': [0.0, 0.0, 0.0],
        },
        'cash_flow': {
            'Operating Cash Flow': [30.0, 28.0, 26.0],
            'Capital Expenditure': [-15.0, -14.0, -13.0],
            'Cash Dividends Paid': [-10.0, -9.0, -8.0],
            'Common Stock Payments': [-2.0, -2.0, -1.0],
        }
    }


@pytest.fixture
def create_test_company(tmp_path, sample_financial_data):
    """
    Factory fixture that creates a test company folder with CSV files.
    
    Usage:
        def test_something(create_test_company):
            company_folder = create_test_company("TestCo")
            # use company_folder...
    """
    def _create_company(company_name: str, data=None):
        """
        Create a company folder with financial statement CSVs.
        
        Args:
            company_name: Name of the company
            data: Optional custom financial data (uses sample_financial_data if None)
        
        Returns:
            Path to the company folder
        """
        if data is None:
            data = sample_financial_data
        
        folder = tmp_path / company_name
        folder.mkdir(exist_ok=True)
        
        cols = data['columns']
        
        # Create income statement CSV  
        # Each row is a financial item, each column is a year
        income_data = {}
        for year_idx, year in enumerate(cols):
            income_data[year] = [data['income_statement'][item][year_idx] for item in data['income_statement'].keys()]
        
        income_df = pd.DataFrame(
            income_data,
            index=list(data['income_statement'].keys())
        )
        income_df.to_csv(folder / "income statement.csv")
        
        # Create balance sheet CSV
        balance_data = {}
        for year_idx, year in enumerate(cols):
            balance_data[year] = [data['balance_sheet'][item][year_idx] for item in data['balance_sheet'].keys()]
        
        balance_df = pd.DataFrame(
            balance_data,
            index=list(data['balance_sheet'].keys())
        )
        balance_df.to_csv(folder / "balance sheet.csv")
        
        # Create cash flow CSV
        cash_data = {}
        for year_idx, year in enumerate(cols):
            cash_data[year] = [data['cash_flow'][item][year_idx] for item in data['cash_flow'].keys()]
        
        cash_df = pd.DataFrame(
            cash_data,
            index=list(data['cash_flow'].keys())
        )
        cash_df.to_csv(folder / "cash flow.csv")
        
        return str(folder)
    
    return _create_company


@pytest.fixture
def minimal_inputs():
    """
    Returns a minimal set of inputs for testing forecast modules.
    """
    return {
        # Year 0 Income Statement
        'revenue_year_0': 100.0,
        'cogs_year_0': 60.0,
        'gross_profit_year_0': 40.0,
        'sga_year_0': 10.0,
        'depreciation_year_0': 5.0,
        'operating_income_year_0': 25.0,
        'interest_expense_year_0': 2.0,
        'pretax_income_year_0': 23.0,
        'tax_provision_year_0': 4.6,
        'net_income_year_0': 18.4,
        'dividends_paid_year_0': 5.0,
        'stock_repurchase_year_0': 0.0,
        
        # Year 0 Balance Sheet
        'cash_year_0': 10.0,
        'accounts_receivable_year_0': 8.0,
        'inventory_year_0': 6.0,
        'current_assets_year_0': 30.0,
        'net_ppe_year_0': 100.0,
        'gross_ppe_year_0': 120.0,
        'accumulated_depreciation_year_0': 20.0,
        'goodwill_year_0': 10.0,
        'intangible_assets_year_0': 5.0,
        'total_assets_year_0': 150.0,
        'accounts_payable_year_0': 5.0,
        'short_term_debt_year_0': 10.0,
        'long_term_debt_year_0': 50.0,
        'current_liabilities_year_0': 20.0,
        'total_liabilities_year_0': 80.0,
        'total_equity_year_0': 70.0,
        'retained_earnings_year_0': 50.0,
        'minority_interest_year_0': 0.0,
        
        # Year 0 Cash Flow
        'operating_cash_flow_year_0': 25.0,
        'capex_year_0': 10.0,
        
        # Forecast Assumptions
        'revenue_growth': [0.05, 0.05, 0.05, 0.05],
        'inflation_rate': 0.025,
        'cogs_pct_revenue': 0.60,
        'sga_pct_revenue': 0.10,
        'capex_pct_revenue': 0.10,
        'depreciation_rate': 0.05,
        'tax_rate': 0.20,
        'payout_ratio': 0.30,
        
        # Working Capital
        'ar_pct_revenue': 0.08,
        'inventory_pct_cogs': 0.10,
        'ap_pct_cogs': 0.08,
        'min_cash_pct_revenue': 0.10,
        
        # Financing
        'cost_of_debt': 0.05,
        'return_st_investment': 0.02,
        'pct_financing_with_debt': 0.70,
        'st_loan_years': 1.0,
        'lt_loan_years': 10.0,
    }


@pytest.fixture
def forecast_config():
    """Returns a standard ForecastConfig for testing."""
    from company_forecast.config import ForecastConfig
    return ForecastConfig(n_forecast_years=3, n_input_years=3, base_year=2023)


@pytest.fixture
def model_assumptions():
    """Returns standard ModelAssumptions for testing."""
    from company_forecast.config import ModelAssumptions
    return ModelAssumptions()
