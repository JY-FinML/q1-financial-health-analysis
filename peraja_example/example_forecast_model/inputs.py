"""
Input data module for financial forecasting model.
Handles reading and parsing input data from Excel/CSV files.
"""

import pandas as pd


class InputData:
    """Class to handle all input data for the financial forecast"""
    
    def __init__(self, file_path=None):
        """
        Initialize input data
        
        Args:
            file_path: Path to Excel or CSV file with input data
        """
        self.file_path = file_path
        
        # Fixed inputs
        self.fixed_assets = 45.0
        self.linear_depreciation_years = 4.0
        self.corporate_tax_rate = 0.35
        self.initial_inventory_units = 4.0
        self.initial_purchase_price = 5.0
        self.estimated_overhead_expenses = 22.0
        self.admin_sales_payroll = 24.0
        self.lt_loan_years = 10.0
        self.st_loan_years = 1.0
        
        # Time-varying inputs (by year 1-4)
        self.inflation_rate = [0.06, 0.055, 0.055, 0.05]
        self.real_increase_selling_price = [0.01, 0.01, 0.01, 0.01]
        self.real_increase_purchase_price = [0.005, 0.005, 0.005, 0.01]
        self.real_increase_overhead = [0.005, 0.005, 0.005, 0.005]
        self.real_increase_payroll = [0.015, 0.015, 0.015, 0.015]
        self.increase_sales_volume = [0.00, 0.01, 0.02, 0.02]
        self.real_interest_rate = 0.02
        self.risk_premium_debt = 0.05
        self.risk_premium_st_investment = -0.02
        
        # Policy parameters
        self.promotion_advertising_pct = 0.03
        self.inventory_pct_volume = 0.0833333333
        self.accounts_receivable_pct = 0.05
        self.advance_payments_from_customer_pct = 0.10
        self.accounts_payable_pct = 0.10
        self.advance_payments_to_suppliers_pct = 0.10
        self.payout_ratio = 0.70
        self.pct_sales_as_cash = 0.04
        self.pct_financing_with_debt = 0.70
        self.minimum_cash_required = 13.0
        self.selling_commissions = 0.04
        self.stock_repurchase_pct_depreciation = [0.0, 0.0, 0.0, 0.0]
        
        # Market research data
        self.initial_selling_price = 7.0
        self.elasticity_b = -0.35
        self.elasticity_coefficient_b0 = 100.0
        
        if file_path:
            self.load_from_file(file_path)
    
    def load_from_file(self, file_path):
        """
        Load input data from Excel or CSV file
        
        Args:
            file_path: Path to input file
        """
        # This can be expanded to parse different file formats
        if file_path.endswith('.csv'):
            self._load_from_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            self._load_from_excel(file_path)
    
    def _load_from_csv(self, file_path):
        """Load from CSV file"""
        # Implementation can be added based on CSV structure
        pass
    
    def _load_from_excel(self, file_path):
        """Load from Excel file"""
        # Implementation can be added based on Excel structure
        pass
    
    def get_summary(self):
        """Return a summary of key input parameters"""
        summary = {
            'Fixed Assets': self.fixed_assets,
            'Depreciation Years': self.linear_depreciation_years,
            'Tax Rate': self.corporate_tax_rate,
            'Initial Selling Price': self.initial_selling_price,
            'Minimum Cash': self.minimum_cash_required,
            'Debt Financing %': self.pct_financing_with_debt,
            'Payout Ratio': self.payout_ratio
        }
        return summary
