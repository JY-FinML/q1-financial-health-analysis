"""
Company Configuration File
Defines data paths and parameters for each company
"""
import os

# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Company configurations
COMPANIES = {
    'ProcterGamble': {
        'name': 'Procter & Gamble',
        'ticker': 'PG',
        'data_path': os.path.join(DATA_DIR, 'ProcterGamble'),
        'fiscal_year_end': '06-30',  # June 30
        'base_years': [2022, 2023, 2024],
        'forecast_years': [2025],
    },
    'Costco': {
        'name': 'Costco Wholesale',
        'ticker': 'COST',
        'data_path': os.path.join(DATA_DIR, 'Costco'),
        'fiscal_year_end': '08-31',  # August 31
        'base_years': [2022, 2023, 2024],
        'forecast_years': [2025],
    },
    'CocaCola': {
        'name': 'The Coca-Cola Company',
        'ticker': 'KO',
        'data_path': os.path.join(DATA_DIR, 'CocaCola'),
        'fiscal_year_end': '12-31',  # December 31
        'base_years': [2021, 2022,2023],
        'forecast_years': [2024],
    },
    'McDonalds': {
        'name': "McDonald's Corporation",
        'ticker': 'MCD',
        'data_path': os.path.join(DATA_DIR, 'McDonalds'),
        'fiscal_year_end': '12-31',  # December 31
        'base_years': [2021, 2022, 2023],
        'forecast_years': [2024],
    },
}

# Year-end date mapping
def get_year_end_dates(company_key: str) -> dict:
    """Get fiscal year-end dates for the specified company"""
    config = COMPANIES[company_key]
    fiscal_end = config['fiscal_year_end']
    
    dates = {}
    all_years = config['base_years'] + config['forecast_years']
    
    for year in range(min(all_years) - 2, max(all_years) + 1):
        dates[year] = f"{year}-{fiscal_end}"
    
    return dates

# Get company configuration
def get_company_config(company_key: str) -> dict:
    """Get company configuration"""
    if company_key not in COMPANIES:
        raise ValueError(f"Company {company_key} not found. Available: {list(COMPANIES.keys())}")
    return COMPANIES[company_key]
