"""
Generic Data Loader
Load company financial data from CSV files
"""
import pandas as pd
import os
from typing import Dict, Optional
from .config import get_company_config


def load_csv_data(file_path: str) -> pd.DataFrame:
    """
    Load CSV data and transpose
    
    Args:
        file_path: CSV file path
        
    Returns:
        Transposed DataFrame, index=metric names, columns=dates
    """
    df = pd.read_csv(file_path, index_col=0)
    return df.transpose()


def load_company_data(company_key: str) -> Dict[str, pd.DataFrame]:
    """
    Load all financial data for a company
    
    Args:
        company_key: Company key (e.g., 'ProcterGamble', 'Costco')
        
    Returns:
        Dictionary containing balance_sheet, income_statement, cash_flow
    """
    config = get_company_config(company_key)
    data_path = config['data_path']
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data path not found: {data_path}")
    
    data = {}
    
    # Load balance sheet
    bs_path = os.path.join(data_path, 'balance sheet.csv')
    if os.path.exists(bs_path):
        data['balance_sheet'] = load_csv_data(bs_path)
    else:
        raise FileNotFoundError(f"Balance sheet not found: {bs_path}")
    
    # Load income statement
    is_path = os.path.join(data_path, 'income statement.csv')
    if os.path.exists(is_path):
        data['income_statement'] = load_csv_data(is_path)
    else:
        raise FileNotFoundError(f"Income statement not found: {is_path}")
    
    # Load cash flow statement
    cf_path = os.path.join(data_path, 'cash flow.csv')
    if os.path.exists(cf_path):
        data['cash_flow'] = load_csv_data(cf_path)
    else:
        raise FileNotFoundError(f"Cash flow not found: {cf_path}")
    
    return data


def get_value(df: pd.DataFrame, account: str, date: str) -> float:
    """
    Get value for a specific account and date from DataFrame
    
    Args:
        df: Financial data DataFrame
        account: Account name
        date: Date (e.g., '2023-06-30')
        
    Returns:
        Account value, returns 0 if not found
    """
    try:
        if account in df.columns and date in df.index:
            value = df.loc[date, account]
            # Handle NaN or empty values
            if pd.isna(value):
                return 0.0
            return float(value)
        return 0.0
    except Exception:
        return 0.0


def get_historical_values(df: pd.DataFrame, account: str, dates: list) -> list:
    """
    Get historical values for multiple dates
    
    Args:
        df: Financial data DataFrame
        account: Account name
        dates: List of dates
        
    Returns:
        List of values
    """
    return [get_value(df, account, date) for date in dates]
