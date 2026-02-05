import os
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from data.fetch_yfinance import save_statements, company_names

@pytest.fixture
def mock_ticker():
    mock_df = pd.DataFrame({
        '2023-12-31': [1_000_000, 2_000_000],
        '2022-12-31': [3_000_000, 4_000_000],
        '2021-12-31': [5_000_000, 6_000_000],
        '2020-12-31': [7_000_000, 8_000_000]
    }, index=['Revenue', 'Net Income'])
    mock_ticker = MagicMock()
    mock_ticker.financials = mock_df
    mock_ticker.balancesheet = mock_df
    mock_ticker.cashflow = mock_df
    return mock_ticker

def test_save_statements_creates_files(tmp_path, mock_ticker):
    test_symbols = ['KO']
    test_group = "test_group"
    # Patch base_folder and yfinance.Ticker
    from data import fetch_yfinance
    fetch_yfinance.base_folder = str(tmp_path)
    with patch('yfinance.Ticker', return_value=mock_ticker):
        save_statements(test_symbols, test_group)
    # Check if files are created
    company_folder = os.path.join(tmp_path, test_group, 'CocaCola')
    assert os.path.isdir(company_folder)
    for statement in ["income statement", "balance sheet", "cash flow"]:
        file_path = os.path.join(company_folder, f"{statement}.csv")
        assert os.path.isfile(file_path)
        df = pd.read_csv(file_path, index_col=0)
        assert not df.empty
        # Check if values are converted to millions
        assert df.iloc[0, 0] == 1.0  # 1_000_000 / 1_000_000 = 1

def test_save_statements_multiple_symbols(tmp_path, mock_ticker):
    test_symbols = ['KO', 'COST']
    test_group = ""
    from data import fetch_yfinance
    fetch_yfinance.base_folder = str(tmp_path)
    with patch('yfinance.Ticker', return_value=mock_ticker):
        save_statements(test_symbols, test_group)
    for symbol in test_symbols:
        company_name = company_names[symbol]
        company_folder = os.path.join(tmp_path, test_group, company_name)
        assert os.path.isdir(company_folder)
        for statement in ["income statement", "balance sheet", "cash flow"]:
            file_path = os.path.join(company_folder, f"{statement}.csv")
            assert os.path.isfile(file_path)

def test_save_statements_with_five_columns(tmp_path):
    # Mock df with 5 columns
    mock_df = pd.DataFrame({
        '2023-12-31': [1_000_000, 2_000_000],
        '2022-12-31': [3_000_000, 4_000_000],
        '2021-12-31': [5_000_000, 6_000_000],
        '2020-12-31': [7_000_000, 8_000_000],
        '2019-12-31': [9_000_000, 10_000_000]  # Extra column
    }, index=['Revenue', 'Net Income'])
    mock_ticker = MagicMock()
    mock_ticker.financials = mock_df
    mock_ticker.balancesheet = mock_df
    mock_ticker.cashflow = mock_df
    test_symbols = ['KO']
    test_group = "test_group"
    from data import fetch_yfinance
    fetch_yfinance.base_folder = str(tmp_path)
    with patch('yfinance.Ticker', return_value=mock_ticker):
        save_statements(test_symbols, test_group)
    company_folder = os.path.join(tmp_path, test_group, 'CocaCola')
    file_path = os.path.join(company_folder, "income statement.csv")
    df = pd.read_csv(file_path, index_col=0)
    assert df.shape[1] == 4  # Should keep only first 4 columns
