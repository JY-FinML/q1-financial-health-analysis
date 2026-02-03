"""
Debt Schedule module for company forecasting.
Tracks short-term and long-term loans with payment schedules.
"""

from typing import Dict, List
from .config import ForecastConfig


class DebtSchedule:
    """
    Manages debt schedules including:
    - Short-term debt (typically 1-year maturity)
    - Long-term debt (typically 10-year maturity)
    - Interest and principal payment tracking
    
    Uses the no-circularity approach:
    - Interest is calculated on beginning-of-year balance
    - Principal payments are based on loan terms
    """
    
    def __init__(self, inputs: Dict, config: ForecastConfig):
        """
        Initialize debt schedule
        
        Args:
            inputs: Dictionary of calculated inputs
            config: ForecastConfig object
        """
        self.inputs = inputs
        self.config = config
        self.n_years = config.n_forecast_years
        
        # Loan terms
        self.st_loan_years = inputs.get('st_loan_years', 1.0)
        self.lt_loan_years = inputs.get('lt_loan_years', 10.0)
        
        # Short-term debt tracking
        self.st_beginning_balance = [0]  # Will be updated
        self.st_ending_balance = []
        
        # Long-term debt tracking
        self.lt_beginning_balance = [0]  # Will be updated
        self.lt_ending_balance = []
        
        # Track loans by origination year for LT debt amortization
        self.lt_loans_by_year = []
        self.lt_principal_payments_by_year = []
    
    def initialize_year_0(self, st_debt_0: float, lt_debt_0: float):
        """
        Initialize Year 0 debt from historical data
        
        Args:
            st_debt_0: Historical short-term debt balance
            lt_debt_0: Historical long-term debt balance
        """
        # Year 0 ending balances = historical balances
        self.st_ending_balance.append(st_debt_0)
        self.lt_ending_balance.append(lt_debt_0)
        
        # Track existing LT debt for amortization
        if lt_debt_0 > 0:
            # Assume existing LT debt is partially amortized
            # We'll calculate annual payment based on remaining balance / remaining years
            remaining_years = self.lt_loan_years * 0.7  # Assume 30% already amortized
            self.lt_loans_by_year.append([lt_debt_0])
            annual_payment = lt_debt_0 / remaining_years if remaining_years > 0 else lt_debt_0
            self.lt_principal_payments_by_year.append([annual_payment])
        else:
            self.lt_loans_by_year.append([0])
            self.lt_principal_payments_by_year.append([0])
    
    def update_st_debt(self, year: int, new_loan: float, principal_payment: float):
        """
        Update short-term debt for a year
        
        Args:
            year: Year number (1-4)
            new_loan: New short-term loan taken this year
            principal_payment: Principal payment this year
        """
        # Beginning balance = previous year's ending balance
        beginning = self.st_ending_balance[year - 1]
        self.st_beginning_balance.append(beginning)
        
        # Ending balance = beginning - payment + new loan
        ending = max(0, beginning - principal_payment + new_loan)
        self.st_ending_balance.append(ending)
    
    def update_lt_debt(self, year: int, new_loan: float):
        """
        Update long-term debt for a year
        
        Args:
            year: Year number (1-4)
            new_loan: New long-term loan taken this year
        """
        # Beginning balance = previous year's ending balance
        beginning = self.lt_ending_balance[year - 1]
        self.lt_beginning_balance.append(beginning)
        
        # Track new loan
        if new_loan > 0:
            self.lt_loans_by_year.append([new_loan])
            annual_payment = new_loan / self.lt_loan_years
            self.lt_principal_payments_by_year.append([annual_payment])
        else:
            self.lt_loans_by_year.append([0])
            self.lt_principal_payments_by_year.append([0])
        
        # Calculate principal payment
        principal_payment = self.get_total_lt_principal_payment(year)
        
        # Ending balance = beginning + new loan - principal payment
        ending = max(0, beginning + new_loan - principal_payment)
        self.lt_ending_balance.append(ending)
    
    def get_total_lt_principal_payment(self, year: int) -> float:
        """
        Calculate total LT principal payment for a year
        
        Payment is the sum of amortization from all outstanding loans
        
        Args:
            year: Year number (1-4)
            
        Returns:
            Total principal payment
        """
        total = 0
        
        for orig_year in range(year):
            if orig_year < len(self.lt_principal_payments_by_year):
                payments = self.lt_principal_payments_by_year[orig_year]
                if payments and len(payments) > 0:
                    # Each loan has the same annual payment
                    total += payments[0]
        
        return total
    
    def get_lt_interest_payment(self, year: int, cost_of_debt: float) -> float:
        """
        Calculate LT interest payment for a year
        
        Uses beginning-of-year balance (no circularity)
        
        Args:
            year: Year number (1-4)
            cost_of_debt: Cost of debt rate for this year
            
        Returns:
            Interest payment
        """
        beginning = self.lt_ending_balance[year - 1] if year > 0 else 0
        return beginning * cost_of_debt if beginning > 0 else 0
    
    def get_st_interest_payment(self, year: int, cost_of_debt: float) -> float:
        """
        Calculate ST interest payment for a year
        
        Args:
            year: Year number (1-4)
            cost_of_debt: Cost of debt rate for this year
            
        Returns:
            Interest payment
        """
        beginning = self.st_ending_balance[year - 1] if year > 0 else 0
        return beginning * cost_of_debt if beginning > 0 else 0
    
    def get_summary(self) -> Dict[str, List[float]]:
        """Return debt schedule as a dictionary"""
        return {
            'ST Beginning Balance': self.st_beginning_balance,
            'ST Ending Balance': self.st_ending_balance,
            'LT Beginning Balance': self.lt_beginning_balance,
            'LT Ending Balance': self.lt_ending_balance,
        }
