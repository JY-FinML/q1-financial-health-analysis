"""
Intermediate calculations module.
Computes all intermediate values needed for cash budget and financial statements.
"""


class IntermediateCalculations:
    """
    Handles all intermediate calculations including:
    - Nominal price increases (Fisher equation)
    - Sales volume and revenue forecasts
    - Minimum cash requirements
    - Interest rates
    - Depreciation schedules
    - Inventory and COGS (FIFO method)
    - Administrative & selling expenses
    - Credit sales and advance payments
    """
    
    def __init__(self, inputs, config):
        """
        Initialize intermediate calculations
        
        Args:
            inputs: InputData object with all input parameters
            config: ForecastConfig object
        """
        self.inputs = inputs
        self.config = config
        self.n_years = config.n_years
        
        # Storage for calculated values
        self.nominal_increase_selling = []
        self.nominal_increase_purchasing = []
        self.nominal_increase_overhead = []
        self.nominal_increase_payroll = []
        
        self.selling_price = [inputs.initial_selling_price]
        self.sales_units = []
        self.total_sales_revenue = []
        self.min_cash_required = [inputs.minimum_cash_required]
        
        self.risk_free_rate = []
        self.return_st_investment = []
        self.cost_of_debt = []
        
        # Depreciation
        self.investment_by_year = []
        self.depreciation_by_year = []
        self.total_depreciation = [0]
        self.cumulated_depreciation = [0]
        self.net_fixed_assets = [inputs.fixed_assets]
        self.investment_fixed_assets = [inputs.fixed_assets]
        
        # Inventory
        self.final_inventory_units = [inputs.initial_inventory_units]
        self.initial_inventory_units = [0]
        self.purchases_units = []
        
        self.unit_cost = [inputs.initial_purchase_price]
        self.initial_inventory_value = [0]
        self.purchases_value = []
        self.final_inventory_value = [inputs.initial_inventory_units * inputs.initial_purchase_price]
        self.cogs = []
        
        # Expenses
        self.sales_commissions = []
        self.overhead_expenses = [inputs.estimated_overhead_expenses]
        self.payroll_expenses = [inputs.admin_sales_payroll]
        self.advertising_expenses = []
        self.total_as_expenses = []
        
        # Credit and advance payments
        self.credit_sales = []
        self.advance_payments_from_customers = []
        self.inflow_current_year = []
        
        self.purchases_on_credit = []
        self.advance_payments_to_suppliers = []
        self.purchases_paid_same_year = []
        
        self.sales_revenue_current_year_cash = []
        self.accounts_receivable_inflow = [0]
        self.advance_payments_inflow = []
        self.total_sales_inflows = []
        
        self.purchases_paid_current_year_cash = []
        self.accounts_payable_outflow = [0]
        self.advance_payments_outflow = []
        self.total_purchases_outflows = []
    
    def calculate_all(self):
        """Execute all intermediate calculations in proper order"""
        print("  Calculating intermediate values...")
        self.calculate_nominal_increases()
        self.calculate_sales_and_pricing()
        self.calculate_min_cash()
        self.calculate_interest_rates()
        self.calculate_depreciation()
        self.calculate_inventory_and_purchases()
        self.calculate_expenses()
        self.calculate_credit_and_advances()
        print("  ✓ Intermediate calculations complete")
    
    def calculate_nominal_increases(self):
        """Calculate nominal increases using Fisher equation"""
        for i in range(self.n_years):
            # Fisher equation: (1 + real) * (1 + inflation) - 1
            nom_selling = (1 + self.inputs.real_increase_selling_price[i]) * \
                         (1 + self.inputs.inflation_rate[i]) - 1
            nom_purchasing = (1 + self.inputs.real_increase_purchase_price[i]) * \
                           (1 + self.inputs.inflation_rate[i]) - 1
            nom_overhead = (1 + self.inputs.real_increase_overhead[i]) * \
                         (1 + self.inputs.inflation_rate[i]) - 1
            nom_payroll = (1 + self.inputs.real_increase_payroll[i]) * \
                        (1 + self.inputs.inflation_rate[i]) - 1
            
            self.nominal_increase_selling.append(nom_selling)
            self.nominal_increase_purchasing.append(nom_purchasing)
            self.nominal_increase_overhead.append(nom_overhead)
            self.nominal_increase_payroll.append(nom_payroll)
    
    def calculate_sales_and_pricing(self):
        """Calculate sales units, prices, and revenues"""
        # Year 0: Calculate initial sales units using elasticity
        initial_units = self.inputs.elasticity_coefficient_b0 * \
                       (self.inputs.initial_selling_price ** self.inputs.elasticity_b)
        self.sales_units.append(initial_units)
        
        # Years 1-4
        for i in range(self.n_years):
            # Selling price increases by nominal rate
            price = self.selling_price[i] * (1 + self.nominal_increase_selling[i])
            self.selling_price.append(price)
            
            # Sales units: previous year * (1 + volume increase)
            units = self.sales_units[i] * (1 + self.inputs.increase_sales_volume[i])
            self.sales_units.append(units)
            
            # Total revenue
            revenue = units * price
            self.total_sales_revenue.append(revenue)
    
    def calculate_min_cash(self):
        """Calculate minimum cash required for each year"""
        for i in range(self.n_years):
            # Percentage of sales as cash * total sales revenue
            min_cash = self.inputs.pct_sales_as_cash * self.total_sales_revenue[i]
            self.min_cash_required.append(min_cash)
    
    def calculate_interest_rates(self):
        """Calculate interest rates using Fisher equation"""
        for i in range(self.n_years):
            # Risk-free rate
            rf = (1 + self.inputs.real_interest_rate) * \
                 (1 + self.inputs.inflation_rate[i]) - 1
            self.risk_free_rate.append(rf)
            
            # Return on ST investment
            self.return_st_investment.append(rf + self.inputs.risk_premium_st_investment)
            
            # Cost of debt
            self.cost_of_debt.append(rf + self.inputs.risk_premium_debt)
    
    def calculate_depreciation(self):
        """Calculate depreciation schedule and fixed asset investments"""
        depr_years = self.inputs.linear_depreciation_years
        
        # Initialize tracking arrays
        self.investment_by_year = [self.inputs.fixed_assets]
        self.depreciation_by_year = [[0] * (self.n_years + 1) for _ in range(self.n_years + 1)]
        
        # Year 0 investment depreciation (starts in year 1)
        for year in range(1, self.n_years + 1):
            self.depreciation_by_year[0][year] = self.inputs.fixed_assets / depr_years
        
        # Calculate for each year
        for year in range(1, self.n_years + 1):
            # Total depreciation this year (calculated first)
            total_depr = sum(self.depreciation_by_year[inv_year][year] 
                           for inv_year in range(year + 1))
            self.total_depreciation.append(total_depr)
            
            # Investment to replace THIS year's depreciation
            investment_constant = total_depr
            
            # Investment for growth
            prev_net_fa = self.net_fixed_assets[year - 1]
            if year < self.n_years:
                growth_factor = 1 + self.inputs.increase_sales_volume[year]
            else:
                growth_factor = 1
            investment_growth = prev_net_fa * (growth_factor - 1)
            
            # Total investment
            new_investment = investment_constant + investment_growth
            self.investment_by_year.append(new_investment)
            self.investment_fixed_assets.append(new_investment)
            
            # Depreciation for this year's investment (starts next year)
            if year < self.n_years:
                for future_year in range(year + 1, self.n_years + 1):
                    self.depreciation_by_year[year][future_year] = new_investment / depr_years
            
            # Cumulated depreciation
            cum_depr = self.cumulated_depreciation[year - 1] + total_depr
            self.cumulated_depreciation.append(cum_depr)
            
            # Net fixed assets
            net_fa = prev_net_fa + new_investment - total_depr
            self.net_fixed_assets.append(net_fa)
    
    def calculate_inventory_and_purchases(self):
        """Calculate inventory levels and purchases (FIFO method)"""
        # Units
        for i in range(self.n_years):
            # Final inventory as % of sales volume
            final_inv = self.sales_units[i + 1] * self.inputs.inventory_pct_volume
            self.final_inventory_units.append(final_inv)
            
            # Initial inventory = previous final
            initial_inv = self.final_inventory_units[i]
            self.initial_inventory_units.append(initial_inv)
            
            # Purchases = sales + final - initial
            purchases = self.sales_units[i + 1] + final_inv - initial_inv
            self.purchases_units.append(purchases)
        
        # Valuation (FIFO)
        for i in range(self.n_years):
            # Unit cost increases by nominal rate
            cost = self.unit_cost[i] * (1 + self.nominal_increase_purchasing[i])
            self.unit_cost.append(cost)
            
            # Initial inventory value (at previous cost)
            initial_inv_val = self.initial_inventory_units[i + 1] * self.unit_cost[i]
            self.initial_inventory_value.append(initial_inv_val)
            
            # Purchases value (at current cost)
            purchases_val = self.purchases_units[i] * cost
            self.purchases_value.append(purchases_val)
            
            # Final inventory value (at current cost)
            final_inv_val = self.final_inventory_units[i + 1] * cost
            self.final_inventory_value.append(final_inv_val)
            
            # COGS = initial + purchases - final
            cogs = initial_inv_val + purchases_val - final_inv_val
            self.cogs.append(cogs)
    
    def calculate_expenses(self):
        """Calculate administrative and selling expenses"""
        for i in range(self.n_years):
            # Sales commissions
            commissions = self.total_sales_revenue[i] * self.inputs.selling_commissions
            self.sales_commissions.append(commissions)
            
            # Overhead expenses
            overhead = self.overhead_expenses[i] * (1 + self.nominal_increase_overhead[i])
            self.overhead_expenses.append(overhead)
            
            # Payroll expenses
            payroll = self.payroll_expenses[i] * (1 + self.nominal_increase_payroll[i])
            self.payroll_expenses.append(payroll)
            
            # Advertising
            advertising = self.total_sales_revenue[i] * self.inputs.promotion_advertising_pct
            self.advertising_expenses.append(advertising)
            
            # Total A&S expenses
            total_as = commissions + overhead + payroll + advertising
            self.total_as_expenses.append(total_as)
    
    def calculate_credit_and_advances(self):
        """Calculate credit sales and advance payment disaggregation"""
        # Sales disaggregation
        for i in range(self.n_years):
            revenue = self.total_sales_revenue[i]
            credit = revenue * self.inputs.accounts_receivable_pct
            advance = revenue * self.inputs.advance_payments_from_customer_pct
            inflow = revenue - credit - advance
            
            self.credit_sales.append(credit)
            self.advance_payments_from_customers.append(advance)
            self.inflow_current_year.append(inflow)
        
        # Purchases disaggregation
        for i in range(self.n_years):
            purchases = self.purchases_value[i]
            credit = purchases * self.inputs.accounts_payable_pct
            advance = purchases * self.inputs.advance_payments_to_suppliers_pct
            paid_same = purchases - credit - advance
            
            self.purchases_on_credit.append(credit)
            self.advance_payments_to_suppliers.append(advance)
            self.purchases_paid_same_year.append(paid_same)
        
        # Cash flows from sales
        # Year 0: Only advance payment (no sales yet)
        self.advance_payments_inflow.append(self.advance_payments_from_customers[0])
        
        for i in range(self.n_years):
            current_cash = self.inflow_current_year[i]
            self.sales_revenue_current_year_cash.append(current_cash)
            
            # AR from previous year
            ar_inflow = self.credit_sales[i - 1] if i > 0 else 0
            self.accounts_receivable_inflow.append(ar_inflow)
            
            # Advance payments: received for next year's sales
            # Year 1 (i=0): advance for Year 2 (index 1)
            # Year 4 (i=3): advance for Year 5 (doesn't exist, so 0)
            adv_inflow = self.advance_payments_from_customers[i + 1] if i < self.n_years - 1 else 0
            self.advance_payments_inflow.append(adv_inflow)
            
            total_inflow = current_cash + ar_inflow + adv_inflow
            self.total_sales_inflows.append(total_inflow)
        
        # Cash flows for purchases
        # Year 0: Only advance payment (no purchases cash flow yet)
        self.advance_payments_outflow.append(self.advance_payments_to_suppliers[0])
        
        for i in range(self.n_years):
            current_cash = self.purchases_paid_same_year[i]
            self.purchases_paid_current_year_cash.append(current_cash)
            
            # AP from previous year
            ap_outflow = self.purchases_on_credit[i - 1] if i > 0 else 0
            self.accounts_payable_outflow.append(ap_outflow)
            
            # Advance payments to suppliers (paid for next year)
            # Year 1 (i=0): advance for Year 2 (index 1)
            # Year 4 (i=3): advance for Year 5 (doesn't exist, so 0)
            adv_outflow = self.advance_payments_to_suppliers[i + 1] if i < self.n_years - 1 else 0
            self.advance_payments_outflow.append(adv_outflow)
            
            total_outflow = current_cash + ap_outflow + adv_outflow
            self.total_purchases_outflows.append(total_outflow)
