"""
Debt schedule module.
Tracks short-term and long-term loans with payment schedules.
"""


class DebtSchedule:
    """
    Manages debt schedules including:
    - Short-term loans (1-year maturity)
    - Long-term loans (10-year maturity)
    - Interest and principal payment tracking
    """
    
    def __init__(self, inputs, config):
        """
        Initialize debt schedule
        
        Args:
            inputs: InputData object
            config: ForecastConfig object
        """
        self.inputs = inputs
        self.config = config
        self.n_years = config.n_years
        
        # Short-term debt
        self.st_beginning_balance = [0]
        self.st_ending_balance = []
        
        # Long-term debt
        self.lt_beginning_balance = [0]
        self.lt_ending_balance = []
        
        # Track loans by origination year
        self.lt_loans_by_year = []
        self.lt_principal_payments_by_year = []
    
    def initialize_year_0_loans(self, st_loan_0, lt_loan_0):
        """
        Initialize Year 0 loan tracking arrays
        
        Args:
            st_loan_0: Year 0 short-term loan
            lt_loan_0: Year 0 long-term loan
        """
        # Initialize ST debt ending balance for year 0
        self.st_ending_balance.append(st_loan_0)
        
        # Initialize LT debt ending balance for year 0
        self.lt_ending_balance.append(lt_loan_0)
        
        # Initialize LT loan tracking arrays with Year 0 loan
        if lt_loan_0 > 0:
            self.lt_loans_by_year = [[lt_loan_0]]
            # Year 0 loan payment starts in Year 1
            year_0_payment = lt_loan_0 / self.inputs.lt_loan_years
            self.lt_principal_payments_by_year = [[year_0_payment]]
    
    def update_st_debt(self, year, new_loan, principal_payment):
        """
        Update short-term debt for a year
        
        Args:
            year: Year number (1-4)
            new_loan: New short-term loan taken this year
            principal_payment: Principal payment this year
        """
        i = year - 1
        # ending_balance array now includes year 0, so use year-1 as index
        beginning = self.st_ending_balance[year - 1]
        ending = beginning - principal_payment + new_loan
        
        self.st_beginning_balance.append(beginning)
        self.st_ending_balance.append(ending)
    
    def update_lt_debt(self, year, new_loan):
        """
        Update long-term debt for a year
        
        Args:
            year: Year number (1-4)
            new_loan: New long-term loan taken this year
        """
        i = year - 1
        # ending_balance array now includes year 0, so use year-1 as index
        beginning = self.lt_ending_balance[year - 1]
        
        self.lt_beginning_balance.append(beginning)
        
        # Track this year's new loan
        # Add new row for this year's loan
        # Note: payment array starts empty, payments will be added for future years
        self.lt_loans_by_year.append([new_loan])
        self.lt_principal_payments_by_year.append([])
        
        # Calculate payments for all outstanding loans (including this year's new loan for future years)
        for orig_year in range(year + 1):  # Include current year's loan
            if orig_year < len(self.lt_loans_by_year):
                orig_loan = self.lt_loans_by_year[orig_year][0]
                if orig_loan > 0:
                    payment = orig_loan / self.inputs.lt_loan_years
                    self.lt_principal_payments_by_year[orig_year].append(payment)
        
        # Calculate total principal payment
        principal_payment = self.get_total_lt_principal_payment(year)
        
        ending = beginning + new_loan - principal_payment
        self.lt_ending_balance.append(ending)
    
    def get_total_lt_principal_payment(self, year):
        """
        Get total LT principal payment for a year
        
        Args:
            year: Year number (1-4)
            
        Returns:
            Total principal payment
        """
        # Payments start from the year after loan origination
        # For Year 1: pay Year 0 loan (payment[0] = Year 1 payment)
        # For Year 2: pay Year 0 loan (payment[1]) + Year 1 loan (payment[0])
        
        total = 0
        for orig_year in range(year):
            if orig_year < len(self.lt_principal_payments_by_year):
                payments = self.lt_principal_payments_by_year[orig_year]
                # payment_index represents which payment period this is for this loan
                # For orig_year=0, Year 1 uses index 0, Year 2 uses index 1, etc.
                payment_index = year - orig_year - 1
                if payment_index < len(payments):
                    total += payments[payment_index]
        
        return total
    
    def get_lt_interest_payment(self, year, cost_of_debt):
        """
        Get LT interest payment for a year
        
        Args:
            year: Year number (1-4)
            cost_of_debt: Cost of debt rate for this year
            
        Returns:
            Interest payment
        """
        # Use ending balance from previous year as beginning balance
        # lt_ending_balance includes Year 0, so use year-1 as index
        beginning = self.lt_ending_balance[year - 1] if year - 1 < len(self.lt_ending_balance) else 0
        return beginning * cost_of_debt if beginning > 0 else 0
