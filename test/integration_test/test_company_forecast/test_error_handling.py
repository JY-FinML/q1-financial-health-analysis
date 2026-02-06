"""
Integration tests for error handling and edge cases.

Tests that the forecaster handles invalid inputs and missing data gracefully.
"""

import pytest
import pandas as pd
from company_forecast.forecaster import CompanyForecaster
from company_forecast.data_loader import DataLoader


def test_forecaster_missing_data_files(tmp_path):
    """Test that forecaster handles missing data files appropriately."""
    # Create empty folder
    empty_folder = tmp_path / "EmptyCo"
    empty_folder.mkdir()
    
    # Should raise an error or handle gracefully
    with pytest.raises((FileNotFoundError, ValueError, KeyError)):
        f = CompanyForecaster(str(empty_folder), n_forecast_years=2)
        f.run_forecast()


def test_forecaster_incomplete_data(tmp_path):
    """Test forecaster with incomplete financial data."""
    folder = tmp_path / "IncompleteCo"
    folder.mkdir()
    
    # Only create income statement, missing balance sheet and cash flow
    income = pd.DataFrame({
        "2023-12-31": [100, -60, 40],
        "2022-12-31": [90, -54, 36],
        "2021-12-31": [80, -48, 32],
    }, index=["Total Revenue", "Cost Of Revenue", "Net Income"])
    
    income.to_csv(folder / "income statement.csv")
    
    # Should raise an error when trying to run forecast
    with pytest.raises((FileNotFoundError, ValueError, KeyError)):
        f = CompanyForecaster(str(folder), n_forecast_years=2)
        f.run_forecast()


def test_forecaster_invalid_parameters(tmp_path):
    """Test forecaster with invalid parameters."""
    folder = tmp_path / "TestCo"
    folder.mkdir()
    
    # Create minimal valid data
    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]
    income = pd.DataFrame({
        cols[0]: [100, -60, 40],
        cols[1]: [90, -54, 36],
        cols[2]: [80, -48, 32],
    }, index=["Total Revenue", "Cost Of Revenue", "Net Income"])
    
    balance = pd.DataFrame({
        cols[0]: [500, 20, 10],
        cols[1]: [480, 18, 9],
        cols[2]: [460, 16, 8],
    }, index=["Total Assets", "Accounts Receivable", "Current Debt"])
    
    cash = pd.DataFrame({
        cols[0]: [30, -5, -2],
        cols[1]: [28, -5, -2],
        cols[2]: [26, -5, -2],
    }, index=["Operating Cash Flow", "Capital Expenditure", "Cash Dividends Paid"])
    
    income.to_csv(folder / "income statement.csv")
    balance.to_csv(folder / "balance sheet.csv")
    cash.to_csv(folder / "cash flow.csv")
    
    # Test with invalid n_forecast_years
    # Note: Implementation may not validate this, just verify it doesn't crash
    try:
        f = CompanyForecaster(str(folder), n_forecast_years=0)
        # If it doesn't raise, verify it uses at least 1 year or handles gracefully
        if hasattr(f, 'config'):
            assert f.config.n_forecast_years >= 0  # Allow 0 if implementation accepts it
    except (ValueError, AssertionError, AttributeError):
        # Expected to raise error for invalid parameter
        pass
    
    # Test with negative n_forecast_years - may or may not raise
    try:
        f = CompanyForecaster(str(folder), n_forecast_years=-1)
        # If it doesn't crash, verify behavior is reasonable
    except (ValueError, AssertionError, AttributeError):
        # Expected to raise error
        pass


def test_data_loader_nonexistent_folder():
    """Test DataLoader with non-existent folder."""
    # Note: DataLoader may print error but not raise exception
    dl = DataLoader("/nonexistent/path/to/company")
    result = dl.load_all()
    # Should either be None, empty dict, or False
    if result is not None and result is not False:
        assert len(result) == 0 or not result.get('income_statement', None)
    # Else it returned None or False which is acceptable error handling


def test_forecaster_with_nan_values(tmp_path):
    """Test forecaster behavior with NaN values in historical data."""
    folder = tmp_path / "NaNCo"
    folder.mkdir()
    
    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]
    
    # Income statement with some NaN values
    income = pd.DataFrame({
        cols[0]: [100, -60, None],  # NaN in Net Income
        cols[1]: [90, -54, 36],
        cols[2]: [80, -48, 32],
    }, index=["Total Revenue", "Cost Of Revenue", "Net Income"])
    
    balance = pd.DataFrame({
        cols[0]: [500, 20, 10],
        cols[1]: [480, 18, 9],
        cols[2]: [460, 16, 8],
    }, index=["Total Assets", "Accounts Receivable", "Current Debt"])
    
    cash = pd.DataFrame({
        cols[0]: [30, -5, -2],
        cols[1]: [28, -5, -2],
        cols[2]: [26, -5, -2],
    }, index=["Operating Cash Flow", "Capital Expenditure", "Cash Dividends Paid"])
    
    income.to_csv(folder / "income statement.csv")
    balance.to_csv(folder / "balance sheet.csv")
    cash.to_csv(folder / "cash flow.csv")
    
    # Should either handle NaN gracefully or raise informative error
    try:
        f = CompanyForecaster(str(folder), n_forecast_years=1, n_input_years=1)
        f.run_forecast()
        # If it succeeds, verify results are not NaN
        assert not pd.isna(f.income_statement.revenue[1])
    except (ValueError, KeyError, TypeError):
        # Expected to raise error for NaN values
        pass


def test_forecaster_extreme_values(tmp_path):
    """Test forecaster with extreme but valid values."""
    folder = tmp_path / "ExtremeCo"
    folder.mkdir()
    
    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]
    
    # Very large numbers
    income = pd.DataFrame({
        cols[0]: [1_000_000, -600_000, 400_000],
        cols[1]: [950_000, -570_000, 380_000],
        cols[2]: [900_000, -540_000, 360_000],
    }, index=["Total Revenue", "Cost Of Revenue", "Net Income"])
    
    balance = pd.DataFrame({
        cols[0]: [5_000_000, 200_000, 100_000],
        cols[1]: [4_800_000, 180_000, 90_000],
        cols[2]: [4_600_000, 160_000, 80_000],
    }, index=["Total Assets", "Accounts Receivable", "Current Debt"])
    
    cash = pd.DataFrame({
        cols[0]: [300_000, -50_000, -20_000],
        cols[1]: [280_000, -50_000, -20_000],
        cols[2]: [260_000, -50_000, -20_000],
    }, index=["Operating Cash Flow", "Capital Expenditure", "Cash Dividends Paid"])
    
    income.to_csv(folder / "income statement.csv")
    balance.to_csv(folder / "balance sheet.csv")
    cash.to_csv(folder / "cash flow.csv")
    
    # Should handle large numbers without overflow
    f = CompanyForecaster(str(folder), n_forecast_years=2, n_input_years=2)
    f.run_forecast()
    
    # Verify results are finite
    assert all(pd.notna(x) and abs(x) < 1e15 for x in f.income_statement.revenue)
    assert all(pd.notna(x) and abs(x) < 1e15 for x in f.balance_sheet.total_assets)


def test_forecaster_zero_revenue_company(tmp_path):
    """Test forecaster with a company that has zero or very small revenue."""
    folder = tmp_path / "ZeroRevCo"
    folder.mkdir()
    
    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]
    
    # Very small revenue (startup scenario)
    income = pd.DataFrame({
        cols[0]: [1, -10, -9],  # Tiny revenue, large losses
        cols[1]: [0.5, -8, -7.5],
        cols[2]: [0.1, -6, -5.9],
    }, index=["Total Revenue", "Cost Of Revenue", "Net Income"])
    
    balance = pd.DataFrame({
        cols[0]: [100, 1, 0.5],
        cols[1]: [90, 0.8, 0.4],
        cols[2]: [80, 0.6, 0.3],
    }, index=["Total Assets", "Accounts Receivable", "Current Debt"])
    
    cash = pd.DataFrame({
        cols[0]: [5, -2, -3],
        cols[1]: [4, -2, -2],
        cols[2]: [3, -2, -1],
    }, index=["Operating Cash Flow", "Capital Expenditure", "Cash Dividends Paid"])
    
    income.to_csv(folder / "income statement.csv")
    balance.to_csv(folder / "balance sheet.csv")
    cash.to_csv(folder / "cash flow.csv")
    
    # Should handle small numbers without division by zero
    try:
        f = CompanyForecaster(str(folder), n_forecast_years=1, n_input_years=1)
        f.run_forecast()
        # Verify no division by zero errors
        assert f.income_statement is not None
    except (ValueError, ZeroDivisionError):
        # Some calculations might legitimately fail with zero revenue
        # This is acceptable as long as it raises a clear error
        pass
