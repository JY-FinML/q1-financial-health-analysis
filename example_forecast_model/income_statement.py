"""
Income statement module.
Calculates revenues, expenses, and net income.
"""


class IncomeStatement:
    """
    Handles income statement calculations including:
    - Sales revenues
    - Cost of goods sold (COGS)
    - Gross income
    - Operating expenses
    - EBIT, EBT
    - Income taxes
    - Net income
    - Dividends
    """
    
    def __init__(self, inputs, config, intermediate):
        """
        Initialize income statement
        
        Args:
            inputs: InputData object
            config: ForecastConfig object
            intermediate: IntermediateCalculations object
        """
        self.inputs = inputs
        self.config = config
        self.intermediate = intermediate
        self.n_years = config.n_years
        
        # Income statement items
        self.sales_revenues = []
        self.cogs = []
        self.gross_income = []
        self.as_expenses = []
        self.depreciation = []
        self.ebit = []
        self.interest_payments = []
        self.st_investment_return = []
        self.ebt = []
        self.income_taxes = []
        self.net_income = []
        self.next_year_dividends = []
        self.cumulated_retained_earnings = [0]
    
    def calculate_year(self, year, cash_budget, debt_schedule):
        """
        Calculate income statement for a specific year
        
        Args:
            year: Year number (1-4)
            cash_budget: CashBudget object with calculated values
            debt_schedule: DebtSchedule object with beginning balances
        """
        i = year - 1
        
        # Revenue and COGS
        sales_rev = self.intermediate.total_sales_revenue[i]
        cogs = self.intermediate.cogs[i]
        gross_income = sales_rev - cogs
        
        self.sales_revenues.append(sales_rev)
        self.cogs.append(cogs)
        self.gross_income.append(gross_income)
        
        # Operating expenses
        as_exp = self.intermediate.total_as_expenses[i]
        depr = self.intermediate.total_depreciation[year]
        ebit = gross_income - as_exp - depr
        
        self.as_expenses.append(as_exp)
        self.depreciation.append(depr)
        self.ebit.append(ebit)
        
        # Interest payments: calculate from previous year's ending debt balance
        # debt_schedule ending_balance includes Year 0, so use year-1 as index
        st_beginning = debt_schedule.st_ending_balance[year - 1] if len(debt_schedule.st_ending_balance) > year - 1 else 0
        lt_beginning = debt_schedule.lt_ending_balance[year - 1] if len(debt_schedule.lt_ending_balance) > year - 1 else 0
        cost_of_debt = self.intermediate.cost_of_debt[i]
        
        st_interest = st_beginning * cost_of_debt if st_beginning > 0 else 0
        lt_interest = lt_beginning * cost_of_debt if lt_beginning > 0 else 0
        interest_payments = st_interest + lt_interest
        
        # ST investment return (from previous year if exists)
        # For year 1, no prior investment; for year 2+, use previous year's investment
        st_inv_return = 0
        if year > 1 and len(cash_budget.st_investment) >= year:
            prev_investment = cash_budget.st_investment[year - 1]
            st_inv_return = prev_investment * self.intermediate.return_st_investment[i] if prev_investment > 0 else 0
        
        self.interest_payments.append(interest_payments)
        self.st_investment_return.append(st_inv_return)
        
        # EBT and taxes
        ebt = ebit - interest_payments + st_inv_return
        income_tax = max(0, ebt * self.inputs.corporate_tax_rate)
        net_income = ebt - income_tax
        
        self.ebt.append(ebt)
        self.income_taxes.append(income_tax)
        self.net_income.append(net_income)
        
        # Dividends
        next_yr_dividends = net_income * self.inputs.payout_ratio
        self.next_year_dividends.append(next_yr_dividends)
        
        # Cumulated Retained Earnings = prev year cumulated RE + prev year NI - prev year dividends
        # Both net_income and cumulated_retained_earnings include Year 0:
        # - net_income[0] = Year 0 NI = 0
        # - net_income[1] = Year 1 NI
        # - cumulated_retained_earnings[0] = Year 0 cum RE = 0
        # - cumulated_retained_earnings[1] = Year 1 cum RE
        # For Year N (this is year parameter), we need:
        # - prev_cum_re = cumulated_retained_earnings[year - 1] (Year N-1)
        # - prev_ni = net_income[year - 1] (Year N-1)
        # - prev_div = next_year_dividends[year - 2] if year > 1 (Year N-1 dividends, index N-2)
        prev_cumulated_re = self.cumulated_retained_earnings[year - 1]
        prev_year_ni = self.net_income[year - 1]  # Year N-1 NI has index N-1
        prev_year_div = self.next_year_dividends[year - 2] if year > 1 else 0  # Year N-1 dividends has index N-2
        cum_retained = prev_cumulated_re + prev_year_ni - prev_year_div
        
        self.cumulated_retained_earnings.append(cum_retained)
