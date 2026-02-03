"""
Balance sheet module.
Compiles balance sheet from all other calculations.
"""


class BalanceSheet:
    """
    Handles balance sheet compilation including:
    - Assets (current and fixed)
    - Liabilities (current and long-term)
    - Equity
    """
    
    def __init__(self, inputs, config):
        """
        Initialize balance sheet
        
        Args:
            inputs: InputData object
            config: ForecastConfig object
        """
        self.inputs = inputs
        self.config = config
        self.n_years = config.n_years
        
        # Assets
        self.cash = [inputs.minimum_cash_required]
        self.accounts_receivable = [0]
        self.inventory = []
        self.advance_payments_paid = []
        self.st_investment = [0]
        self.current_assets = []
        self.net_fixed_assets = [inputs.fixed_assets]
        self.total_assets = []
        
        # Liabilities
        self.accounts_payable = [0]
        self.advance_payments_received = []
        self.st_debt = [0]
        self.current_liabilities = []
        self.lt_debt = [0]
        self.total_liabilities = []
        
        # Equity
        self.equity_investment = [inputs.minimum_cash_required]
        self.retained_earnings = [0]
        self.current_year_ni = [0]
        self.repurchase_equity = [0]
        self.total_equity = []
        self.total_liab_equity = []
        self.check_difference = []
    
    def calculate_year_0(self, intermediate, debt_schedule=None):
        """
        Calculate balance sheet for year 0
        
        Args:
            intermediate: IntermediateCalculations object
            debt_schedule: DebtSchedule object (optional, for initial debt)
        """
        # Year 0 assets
        inventory_0 = intermediate.final_inventory_value[0]
        app_0 = intermediate.advance_payments_to_suppliers[0]
        
        self.inventory.append(inventory_0)
        self.advance_payments_paid.append(app_0)
        
        ca0 = (self.cash[0] + self.accounts_receivable[0] + inventory_0 + 
               app_0 + self.st_investment[0])
        self.current_assets.append(ca0)
        
        ta0 = ca0 + self.net_fixed_assets[0]
        self.total_assets.append(ta0)
        
        # Year 0 liabilities - use debt schedule if provided
        apr_0 = intermediate.advance_payments_from_customers[0]
        self.advance_payments_received.append(apr_0)
        
        if debt_schedule and len(debt_schedule.st_ending_balance) > 0:
            st_debt_0 = debt_schedule.st_ending_balance[0]
            lt_debt_0 = debt_schedule.lt_ending_balance[0]
        else:
            st_debt_0 = self.st_debt[0]
            lt_debt_0 = self.lt_debt[0]
        
        self.st_debt[0] = st_debt_0
        self.lt_debt[0] = lt_debt_0
        
        cl0 = self.accounts_payable[0] + apr_0 + st_debt_0
        self.current_liabilities.append(cl0)
        
        tl0 = cl0 + lt_debt_0
        self.total_liabilities.append(tl0)
        
        # Year 0 equity
        te0 = (self.equity_investment[0] + self.retained_earnings[0] + 
               self.current_year_ni[0] - self.repurchase_equity[0])
        self.total_equity.append(te0)
        
        tle0 = tl0 + te0
        self.total_liab_equity.append(tle0)
        
        check0 = tle0 - ta0
        self.check_difference.append(check0)
    
    def calculate_year(self, year, intermediate, cash_budget, debt_schedule, income_statement):
        """
        Calculate balance sheet for a specific year
        
        Args:
            year: Year number (1-4)
            intermediate: IntermediateCalculations object
            cash_budget: CashBudget object
            debt_schedule: DebtSchedule object
            income_statement: IncomeStatement object
        """
        i = year - 1
        
        # Assets
        cash = cash_budget.cumulated_ncb[year]
        ar = intermediate.credit_sales[i]
        inventory = intermediate.final_inventory_value[year]
        app = intermediate.advance_payments_to_suppliers[i] if year < self.n_years else 0
        st_inv = cash_budget.st_investment[year]
        
        self.cash.append(cash)
        self.accounts_receivable.append(ar)
        self.inventory.append(inventory)
        self.advance_payments_paid.append(app)
        self.st_investment.append(st_inv)
        
        current_assets = cash + ar + inventory + app + st_inv
        self.current_assets.append(current_assets)
        
        net_fa = intermediate.net_fixed_assets[year]
        self.net_fixed_assets.append(net_fa)
        
        total_assets = current_assets + net_fa
        self.total_assets.append(total_assets)
        
        # Liabilities
        ap = intermediate.purchases_on_credit[i]
        apr = intermediate.advance_payments_from_customers[i] if year < self.n_years else 0
        st_debt = debt_schedule.st_ending_balance[year]
        
        self.accounts_payable.append(ap)
        self.advance_payments_received.append(apr)
        self.st_debt.append(st_debt)
        
        current_liab = ap + apr + st_debt
        self.current_liabilities.append(current_liab)
        
        lt_debt = debt_schedule.lt_ending_balance[year]
        self.lt_debt.append(lt_debt)
        
        total_liab = current_liab + lt_debt
        self.total_liabilities.append(total_liab)
        
        # Equity
        equity_inv = self.equity_investment[year - 1] + cash_budget.invested_equity[year]
        retained = income_statement.cumulated_retained_earnings[year]
        current_ni = income_statement.net_income[i]
        repurchase = self.repurchase_equity[year - 1] + cash_budget.stock_repurchase[year]
        
        self.equity_investment.append(equity_inv)
        self.retained_earnings.append(retained)
        self.current_year_ni.append(current_ni)
        self.repurchase_equity.append(repurchase)
        
        total_equity = equity_inv + retained + current_ni - repurchase
        self.total_equity.append(total_equity)
        
        total_liab_equity = total_liab + total_equity
        self.total_liab_equity.append(total_liab_equity)
        
        check = total_liab_equity - total_assets
        self.check_difference.append(check)
