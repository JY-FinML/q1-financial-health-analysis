"""
Cash budget module.
Calculates cash flows from operating, investing, financing, and discretionary activities.
"""


class CashBudget:
    """
    Handles cash budget calculations including:
    - Module 1: Operating activities
    - Module 2: Investment activities  
    - Module 3: External financing (loans)
    - Module 4: Transactions with owners
    - Module 5: Discretionary transactions (ST investments)
    """
    
    def calculate_year_0(self, debt_schedule):
        """
        Calculate Year 0 cash budget to determine initial financing needs
        """
        # Year 0 Operating NCB
        # Inflows: advance payments from customers for year 1
        inflow_y0 = self.intermediate.advance_payments_from_customers[0]
        
        # Outflows:
        # 1. Initial inventory purchase (not from intermediate arrays which are for year 1+)
        initial_inventory_purchase = self.inputs.initial_inventory_units * self.inputs.initial_purchase_price
        # 2. Advance payments to suppliers for year 1
        advance_paid_y0 = self.intermediate.advance_payments_to_suppliers[0]
        outflow_y0 = initial_inventory_purchase + advance_paid_y0
        
        operating_ncb_y0 = inflow_y0 - outflow_y0
        
        # Investment NCB
        investment_ncb_y0 = -self.inputs.fixed_assets
        
        # Calculate ST loan (only covers operating shortfall to min_cash)
        min_cash = self.inputs.minimum_cash_required
        prev_cumulated_ncb = 0  # Year -1 cumulated NCB is 0
        st_loan_y0 = max(0, -(prev_cumulated_ncb + operating_ncb_y0 - min_cash))
        
        # Calculate LT loan and equity (70/30 split for investment + any remaining operating shortfall)
        # Total need after ST loan
        ncb_after_st = prev_cumulated_ncb + operating_ncb_y0 + investment_ncb_y0 + st_loan_y0
        remaining_need = max(0, -(ncb_after_st - min_cash))
        
        if remaining_need > 0:
            lt_loan_y0 = remaining_need * self.inputs.pct_financing_with_debt
            equity_y0 = remaining_need * (1 - self.inputs.pct_financing_with_debt)
        else:
            lt_loan_y0 = 0
            equity_y0 = 0
        
        # Year 0 values
        financing_ncb_y0 = st_loan_y0 + lt_loan_y0
        ncb_with_owners_y0 = equity_y0
        year_ncb_y0 = operating_ncb_y0 + investment_ncb_y0 + financing_ncb_y0 + ncb_with_owners_y0
        
        # Store year 0 values (prepend to arrays)
        self.operating_ncb.insert(0, operating_ncb_y0)
        self.investment_ncb.insert(0, investment_ncb_y0)
        self.st_loan.insert(0, st_loan_y0)
        self.lt_loan.insert(0, lt_loan_y0)
        self.financing_ncb.insert(0, financing_ncb_y0)
        self.invested_equity.insert(0, equity_y0)
        self.ncb_with_owners.insert(0, ncb_with_owners_y0)
        self.ncb_previous_modules.insert(0, operating_ncb_y0 + investment_ncb_y0 + financing_ncb_y0 + ncb_with_owners_y0)
        self.discretionary_ncb.insert(0, 0)
        self.year_ncb.insert(0, year_ncb_y0)
        self.cumulated_ncb.insert(0, min_cash)
        
        # Note: Debt schedule Year 0 balances are initialized separately via initialize_year_0_loans()
        
        # Add zero payments for year 0
        self.st_loan_principal_payment.insert(0, 0)
        self.st_loan_interest_payment.insert(0, 0)
        self.total_st_payment.insert(0, 0)
        self.lt_loan_principal_payment.insert(0, 0)
        self.lt_loan_interest_payment.insert(0, 0)
        self.total_loan_payment.insert(0, 0)
        self.dividends_payment.insert(0, 0)
        self.stock_repurchase.insert(0, 0)
        self.payments_to_owners.insert(0, 0)
        self.st_investment_redemption.insert(0, 0)
        self.st_investment_return.insert(0, 0)
        self.st_investment_inflow.insert(0, 0)
        self.st_investment.insert(0, 0)
        
        self.year_0_calculated = True
        
        return st_loan_y0, lt_loan_y0, equity_y0
    
    def __init__(self, inputs, config, intermediate):
        """
        Initialize cash budget
        
        Args:
            inputs: InputData object
            config: ForecastConfig object
            intermediate: IntermediateCalculations object
        """
        self.inputs = inputs
        self.config = config
        self.intermediate = intermediate
        self.n_years = config.n_years
        
        # Module 1: Operating activities
        self.total_inflows = []
        self.total_outflows = []
        self.operating_ncb = []
        
        # Module 2: Investment activities
        self.investment_ncb = []
        
        # Module 3: External financing
        self.st_loan = []
        self.lt_loan = []
        self.st_loan_principal_payment = []
        self.st_loan_interest_payment = []
        self.total_st_payment = []
        self.lt_loan_principal_payment = []
        self.lt_loan_interest_payment = []
        self.total_loan_payment = []
        self.financing_ncb = []
        
        # Module 4: Transactions with owners
        self.invested_equity = []
        self.dividends_payment = []
        self.stock_repurchase = []
        self.payments_to_owners = []
        self.ncb_with_owners = []
        
        # Module 5: Discretionary transactions
        self.st_investment_redemption = []
        self.st_investment_return = []
        self.st_investment_inflow = []
        self.st_investment = []
        self.discretionary_ncb = []
        
        # Summary
        self.ncb_previous_modules = []
        self.year_ncb = []
        self.cumulated_ncb = []
        
        # Year 0 initial values (will be calculated)
        self.year_0_calculated = False
    
    def calculate_year(self, year, debt_schedule, income_statement):
        """
        Calculate cash budget for a specific year
        
        Args:
            year: Year number (1-4)
            debt_schedule: DebtSchedule object
            income_statement: IncomeStatement object
        """
        # Index for arrays that DO NOT include year 0 (intermediate calculations, income_statement)
        i = year - 1
        
        # Module 1: Operating activities
        total_inflows = self.intermediate.total_sales_inflows[i]
        total_outflows = (self.intermediate.total_purchases_outflows[i] + 
                         self.intermediate.total_as_expenses[i])
        
        # Add income tax: use CURRENT year's tax (calculated from current year's income)
        # This represents the tax liability from current year's operations
        current_year_tax = income_statement.income_taxes[year] if year < len(income_statement.income_taxes) else 0
        total_outflows += current_year_tax
        
        operating_ncb = total_inflows - total_outflows
        
        self.total_inflows.append(total_inflows)
        self.total_outflows.append(total_outflows)
        self.operating_ncb.append(operating_ncb)
        
        # Module 2: Investment activities
        investment_fa = self.intermediate.investment_fixed_assets[year]
        investment_ncb = -investment_fa
        self.investment_ncb.append(investment_ncb)
        
        # Module 3: External financing
        prev_cumulated_ncb = self.cumulated_ncb[year - 1]
        min_cash = self.intermediate.min_cash_required[year]
        
        # Short-term loan
        ncb_before_st_loan = prev_cumulated_ncb + operating_ncb
        st_loan = max(0, -(ncb_before_st_loan - min_cash))
        self.st_loan.append(st_loan)
        
        # ST loan payments (from debt schedule)
        # debt_schedule arrays include year 0 at index 0
        st_beginning = debt_schedule.st_ending_balance[year - 1]
        st_principal_payment = st_beginning / self.inputs.st_loan_years
        st_interest_payment = st_beginning * self.intermediate.cost_of_debt[i] if st_beginning > 0 else 0
        total_st_payment = st_principal_payment + st_interest_payment
        
        self.st_loan_principal_payment.append(st_principal_payment)
        self.st_loan_interest_payment.append(st_interest_payment)
        self.total_st_payment.append(total_st_payment)
        
        # Dividends and stock repurchase (from previous year)
        dividends = income_statement.next_year_dividends[i - 1] if year > 1 else 0
        # stock_repurchase_pct_depreciation is indexed from year 0
        stock_repurchase = self.intermediate.total_depreciation[year - 1] * \
                          self.inputs.stock_repurchase_pct_depreciation[year - 1] if year > 1 else 0
        
        self.dividends_payment.append(dividends)
        self.stock_repurchase.append(stock_repurchase)
        
        # ST investment from previous year
        st_inv_redemption = self.st_investment[year - 1]
        st_inv_return = st_inv_redemption * self.intermediate.return_st_investment[i] \
                       if year > 1 and st_inv_redemption > 0 else 0
        st_inv_inflow = st_inv_redemption + st_inv_return
        
        self.st_investment_redemption.append(st_inv_redemption)
        self.st_investment_return.append(st_inv_return)
        self.st_investment_inflow.append(st_inv_inflow)
        
        # Calculate LT loan need
        lt_principal_payment = debt_schedule.get_total_lt_principal_payment(year)
        lt_interest_payment = debt_schedule.get_lt_interest_payment(year, 
                                                                     self.intermediate.cost_of_debt[i])
        
        self.lt_loan_principal_payment.append(lt_principal_payment)
        self.lt_loan_interest_payment.append(lt_interest_payment)
        
        # Calculate LT loan need using the formula:
        # LT loan = pct_financing_with_debt * (accumulated NCB + operation NCB + NCB of investment 
        #           + cash from ST loan + ST investment - total loan payment - dividends 
        #           - repurchase stock - minimal cash)
        
        # Note: ST investment inflow is what we get back, total loan payment includes all debt payments
        # Tax is already included in operating NCB, so no need to subtract it separately
        total_loan_payment = total_st_payment + lt_principal_payment + lt_interest_payment
        
        ncb_for_lt_calc = (prev_cumulated_ncb + operating_ncb + investment_ncb + 
                          st_loan + st_inv_inflow - total_loan_payment - 
                          dividends - stock_repurchase - min_cash)
        
        lt_loan = max(0, -ncb_for_lt_calc * self.inputs.pct_financing_with_debt)
        self.lt_loan.append(lt_loan)
        
        self.total_loan_payment.append(total_loan_payment)
        
        financing_ncb = st_loan + lt_loan - total_loan_payment
        self.financing_ncb.append(financing_ncb)
        
        # Module 4: Transactions with owners
        invested_equity = (lt_loan / self.inputs.pct_financing_with_debt) * \
                         (1 - self.inputs.pct_financing_with_debt)
        payments_to_owners = dividends + stock_repurchase
        ncb_with_owners = invested_equity - payments_to_owners
        
        self.invested_equity.append(invested_equity)
        self.payments_to_owners.append(payments_to_owners)
        self.ncb_with_owners.append(ncb_with_owners)
        
        ncb_prev_modules = operating_ncb + investment_ncb + financing_ncb + ncb_with_owners
        self.ncb_previous_modules.append(ncb_prev_modules)
        
        # Module 5: Discretionary transactions
        # ST investment = accumulated NCB + operating NCB + investment NCB + financing NCB + NCB with owners - minimal cash
        # This is equivalent to: accumulated NCB + NCB prev modules - minimal cash
        if st_loan + lt_loan + invested_equity > 0:
            # If we raised any financing, don't make new ST investment
            st_investment = 0
        else:
            # ST investment based on user's formula
            st_investment = max(0, prev_cumulated_ncb + ncb_prev_modules - min_cash)
        
        self.st_investment.append(st_investment)
        discretionary_ncb = st_inv_inflow - st_investment
        self.discretionary_ncb.append(discretionary_ncb)
        
        year_ncb = ncb_prev_modules + discretionary_ncb
        cumulated_ncb = prev_cumulated_ncb + year_ncb
        
        self.year_ncb.append(year_ncb)
        self.cumulated_ncb.append(cumulated_ncb)
