"""
Data loader module for reading historical financial data from CSV files.
"""

import pandas as pd
import os
from typing import Dict, Optional, Tuple


class DataLoader:
    """
    Loads and parses historical financial data from CSV files.
    Expects:
    - income statement.csv
    - balance sheet.csv
    - cash flow.csv
    """
    
    def __init__(self, company_folder: str):
        """
        Initialize data loader
        
        Args:
            company_folder: Path to folder containing company CSV files
        """
        self.company_folder = company_folder
        self.company_name = os.path.basename(company_folder)
        
        # Raw dataframes
        self.income_statement_df: Optional[pd.DataFrame] = None
        self.balance_sheet_df: Optional[pd.DataFrame] = None
        self.cash_flow_df: Optional[pd.DataFrame] = None
        
        # Processed data (as dictionaries keyed by year)
        self.income_statement: Dict = {}
        self.balance_sheet: Dict = {}
        self.cash_flow: Dict = {}
        
        # Available years
        self.years: list = []
        self.latest_year: Optional[str] = None
        
    def load_all(self) -> bool:
        """
        Load all financial statements
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.income_statement_df = self._load_csv("income statement.csv")
            self.balance_sheet_df = self._load_csv("balance sheet.csv")
            self.cash_flow_df = self._load_csv("cash flow.csv")
            
            # Extract years from columns
            self._extract_years()
            
            # Convert to dictionaries for easier access
            self._process_data()
            
            print(f"✓ Loaded data for {self.company_name}")
            print(f"  Available years: {self.years}")
            
            return True
        except Exception as e:
            print(f"✗ Error loading data for {self.company_name}: {e}")
            return False
    
    def _load_csv(self, filename: str) -> pd.DataFrame:
        """Load a CSV file and set first column as index"""
        filepath = os.path.join(self.company_folder, filename)
        df = pd.read_csv(filepath, index_col=0)
        return df
    
    def _extract_years(self):
        """Extract years from column names"""
        if self.income_statement_df is not None:
            # Columns are dates like "2025-06-30"
            self.all_years = sorted([col[:4] for col in self.income_statement_df.columns], reverse=True)
            self.years = self.all_years.copy()
            self.latest_year = self.years[0] if self.years else None
    
    def set_base_year(self, base_year: str):
        """
        Set the base year (Year 0) for forecasting.
        This filters available years to only include base_year and earlier.
        
        Args:
            base_year: The year to use as Year 0 (e.g., '2023')
        """
        if base_year not in self.all_years:
            raise ValueError(f"Base year {base_year} not available. Available years: {self.all_years}")
        
        # Filter years to include only base_year and earlier
        self.years = [y for y in self.all_years if y <= base_year]
        self.latest_year = base_year
        print(f"  Base year set to {base_year}. Using years: {self.years}")
    
    def _process_data(self):
        """Convert dataframes to dictionaries keyed by year"""
        for df, target_dict in [
            (self.income_statement_df, self.income_statement),
            (self.balance_sheet_df, self.balance_sheet),
            (self.cash_flow_df, self.cash_flow)
        ]:
            if df is not None:
                for col in df.columns:
                    year = col[:4]
                    target_dict[year] = df[col].to_dict()
    
    def get_value(self, statement: str, field: str, year: str = None) -> Optional[float]:
        """
        Get a value from a financial statement
        
        Args:
            statement: 'income', 'balance', or 'cash'
            field: Field name (row label from CSV)
            year: Year string (e.g., '2025'). If None, uses latest year
            
        Returns:
            Value as float, or None if not found
        """
        if year is None:
            year = self.latest_year
            
        data_dict = {
            'income': self.income_statement,
            'balance': self.balance_sheet,
            'cash': self.cash_flow
        }.get(statement, {})
        
        if year not in data_dict:
            return None
            
        value = data_dict[year].get(field)
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        return float(value)
    
    def get_historical_values(self, statement: str, field: str, n_years: int = None) -> Dict[str, float]:
        """
        Get historical values for a field across multiple years
        
        Args:
            statement: 'income', 'balance', or 'cash'
            field: Field name
            n_years: Number of years to retrieve (None = all available)
            
        Returns:
            Dictionary of year -> value
        """
        result = {}
        years_to_use = self.years[:n_years] if n_years else self.years
        
        for year in years_to_use:
            value = self.get_value(statement, field, year)
            if value is not None:
                result[year] = value
                
        return result
    
    def calculate_growth_rate(self, statement: str, field: str, n_years: int = 3) -> Optional[float]:
        """
        Calculate average growth rate for a field
        
        Args:
            statement: 'income', 'balance', or 'cash'
            field: Field name
            n_years: Number of years for calculation
            
        Returns:
            Average growth rate, or None if insufficient data
        """
        values = self.get_historical_values(statement, field, n_years + 1)
        
        if len(values) < 2:
            return None
            
        # Sort by year (newest first)
        sorted_years = sorted(values.keys(), reverse=True)
        growth_rates = []
        
        for i in range(len(sorted_years) - 1):
            current = values[sorted_years[i]]
            previous = values[sorted_years[i + 1]]
            
            if previous != 0 and current != 0:
                growth = (current - previous) / abs(previous)
                growth_rates.append(growth)
        
        if growth_rates:
            return sum(growth_rates) / len(growth_rates)
        return None
    
    def get_latest_balance_sheet(self) -> Dict[str, float]:
        """Get all balance sheet items for the latest year"""
        if self.latest_year:
            return self.balance_sheet.get(self.latest_year, {})
        return {}
    
    def get_latest_income_statement(self) -> Dict[str, float]:
        """Get all income statement items for the latest year"""
        if self.latest_year:
            return self.income_statement.get(self.latest_year, {})
        return {}
    
    def get_latest_cash_flow(self) -> Dict[str, float]:
        """Get all cash flow items for the latest year"""
        if self.latest_year:
            return self.cash_flow.get(self.latest_year, {})
        return {}
    
    def calculate_average(self, statement: str, field: str, n_years: int = 3) -> Optional[float]:
        """
        Calculate average value for a field over multiple years
        
        Args:
            statement: 'income', 'balance', or 'cash'
            field: Field name
            n_years: Number of years to average
            
        Returns:
            Average value, or None if insufficient data
        """
        values = self.get_historical_values(statement, field, n_years)
        if values:
            return sum(values.values()) / len(values)
        return None
    
    def calculate_ratio_average(self, statement: str, numerator_field: str, 
                                denominator_field: str, n_years: int = 3) -> Optional[float]:
        """
        Calculate average ratio over multiple years
        
        Args:
            statement: 'income', 'balance', or 'cash'
            numerator_field: Numerator field name
            denominator_field: Denominator field name
            n_years: Number of years to average
            
        Returns:
            Average ratio, or None if insufficient data
        """
        numerators = self.get_historical_values(statement, numerator_field, n_years)
        denominators = self.get_historical_values(statement, denominator_field, n_years)
        
        ratios = []
        for year in numerators:
            if year in denominators and denominators[year] != 0:
                ratios.append(numerators[year] / denominators[year])
        
        if ratios:
            return sum(ratios) / len(ratios)
        return None
    
    def calculate_cross_statement_ratio(self, num_statement: str, num_field: str,
                                        denom_statement: str, denom_field: str,
                                        n_years: int = 3) -> Optional[float]:
        """
        Calculate average ratio between fields from different statements
        
        Args:
            num_statement: Statement for numerator ('income', 'balance', 'cash')
            num_field: Numerator field name
            denom_statement: Statement for denominator
            denom_field: Denominator field name
            n_years: Number of years to average
            
        Returns:
            Average ratio, or None if insufficient data
        """
        numerators = self.get_historical_values(num_statement, num_field, n_years)
        denominators = self.get_historical_values(denom_statement, denom_field, n_years)
        
        ratios = []
        for year in numerators:
            if year in denominators and denominators[year] != 0:
                ratios.append(numerators[year] / denominators[year])
        
        if ratios:
            return sum(ratios) / len(ratios)
        return None
