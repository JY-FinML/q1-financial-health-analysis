import os
import pandas as pd
import yfinance as yf

company_names = {
    'KO': 'CocaCola',
    'COST': 'Costco',
    'MCD': 'McDonalds',
    'PG': 'ProcterGamble',
}

# Base folder to save statements
base_folder = "data/financial_statements"
os.makedirs(base_folder, exist_ok=True)

def convert_to_millions(df):
    """
    Convert numeric values to millions.
    """
    # Work on a copy to avoid mutating the original DataFrame
    df = df.copy()
    # Get all numeric columns (exclude categorical columns)
    numeric_columns = df.select_dtypes(include=['number']).columns

    # Divide all numeric values by 1,000,000 using .loc to avoid SettingWithCopyWarning
    for col in numeric_columns:
        df.loc[:, col] = df[col] / 1_000_000

    return df

def save_statements(symbols, group_name):
    group_folder = os.path.join(base_folder, group_name)
    os.makedirs(group_folder, exist_ok=True)
    for symbol in symbols:
        company_folder = os.path.join(group_folder, company_names[symbol])
        os.makedirs(company_folder, exist_ok=True)
        ticker = yf.Ticker(symbol)
        # Process and save each statement
        for statement_name, df in {
            "income statement": ticker.financials,
            "balance sheet": ticker.balancesheet,
            "cash flow": ticker.cashflow
        }.items():
            # Work on a copy so converting one statement doesn't affect the others
            df_to_save = df.copy()
            # If there are 5 columns, keep only the first 4. As yfinance only provides data of latest 4 years, if there're more columns, they are filled with nan.
            if df_to_save.shape[1] == 5:
                df_to_save = df_to_save.iloc[:, :4]
            file_path = os.path.join(company_folder, f"{statement_name}.csv")
            df_to_save = convert_to_millions(df_to_save)  # Convert to millions
            df_to_save.to_csv(file_path)
            print(f"Saved {file_path}")

save_statements(['KO','COST', 'MCD', 'PG'], "")