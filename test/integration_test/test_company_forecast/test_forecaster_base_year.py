import pandas as pd
from company_forecast.forecaster import CompanyForecaster


def create_sample_company(tmp_path):
    folder = tmp_path / "BaseCo"
    folder.mkdir()
    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]

    income = pd.DataFrame({
        cols[0]: [120, -72, 48],
        cols[1]: [110, -66, 44],
        cols[2]: [100, -60, 40],
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
    return str(folder)


def test_forecaster_respects_base_year_override(tmp_path):
    """Test that base_year parameter correctly sets the starting year."""
    folder = create_sample_company(tmp_path)
    f = CompanyForecaster(folder, n_forecast_years=1, n_input_years=1, base_year='2022')
    f.run_forecast()
    assert f.config.base_year == 2022
    # ensure modules created
    assert f.income_statement is not None
    assert f.balance_sheet is not None


def test_base_year_affects_year_zero_values(tmp_path):
    """Test that different base_year values produce different Year 0 data."""
    folder = create_sample_company(tmp_path)
    
    # Forecast from 2023
    f1 = CompanyForecaster(folder, n_forecast_years=1, n_input_years=1, base_year='2023')
    f1.run_forecast()
    
    # Forecast from 2022
    f2 = CompanyForecaster(folder, n_forecast_years=1, n_input_years=1, base_year='2022')
    f2.run_forecast()
    
    # Year 0 values should be different (2023 vs 2022 historical data)
    assert f1.income_statement.revenue[0] != f2.income_statement.revenue[0]
    assert f1.balance_sheet.total_assets[0] != f2.balance_sheet.total_assets[0]
    
    # Verify the actual values match the historical data
    assert f1.income_statement.revenue[0] == 120  # 2023 revenue
    assert f2.income_statement.revenue[0] == 110  # 2022 revenue
