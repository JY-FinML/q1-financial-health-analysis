import os
import pandas as pd
from company_forecast.data_loader import DataLoader


def _write_csv(folder, name, df):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    df.to_csv(path)


def create_sample_company(tmp_path):
    folder = tmp_path / "SampleCo"
    folder.mkdir()

    cols = ["2023-12-31", "2022-12-31", "2021-12-31"]
    income = pd.DataFrame({
        cols[0]: [121, 110, 100],
        cols[1]: [110, 100, 90],
        cols[2]: [100, 90, 80],
    }, index=["Total Revenue", "Cost Of Revenue", "Net Income"])

    balance = pd.DataFrame({
        cols[0]: [50, 20, 10],
        cols[1]: [45, 18, 9],
        cols[2]: [40, 16, 8],
    }, index=["Total Assets", "Accounts Receivable", "Current Debt"])

    cash = pd.DataFrame({
        cols[0]: [5, -2],
        cols[1]: [4, -1],
        cols[2]: [3, -1],
    }, index=["Operating Cash Flow", "Capital Expenditure"])

    income.to_csv(folder / "income statement.csv")
    balance.to_csv(folder / "balance sheet.csv")
    cash.to_csv(folder / "cash flow.csv")

    return str(folder)


def test_data_loader_basic(tmp_path):
    folder = create_sample_company(tmp_path)
    dl = DataLoader(folder)
    assert dl.load_all() is True
    # latest year should be '2023'
    assert dl.latest_year == '2023'
    # get_value
    revenue = dl.get_value('income', 'Total Revenue', '2023')
    assert revenue == 121
    # growth rate (should compute something > 0)
    g = dl.calculate_growth_rate('income', 'Total Revenue', n_years=2)
    assert g is not None
    # historical values
    hist = dl.get_historical_values('income', 'Total Revenue')
    assert '2023' in hist
