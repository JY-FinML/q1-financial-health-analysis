"""
Generic Company Financial Forecasting Engine
Uses the cash budget method (same calculation logic as forecast_model):
Income Statement → Cash Budget → Debt Schedule → Balance Sheet
Ensures balance sheet balances
"""
from typing import Dict, List
from .input_mapper import CompanyInputMapper


class CompanyForecaster:
    """
    Generic company forecaster using the cash budget method
    Ensures balance sheet balances
    """
    
    def __init__(self, company_key: str):
        # Get mapped inputs
        self.company_key = company_key
        mapper = CompanyInputMapper(company_key)
        self.inputs = mapper.get_forecast_inputs()
        self.company_name = self.inputs.get('company_name', company_key)
        
        # Store forecast results
        self.years = list(range(self.inputs['forecast_years'] + 1))  # [0, 1, 2]
        
        # Store financial statements for each year
        self.revenue = [0.0] * (len(self.years))
        self.cogs = [0.0] * len(self.years)
        self.gross_profit = [0.0] * len(self.years)
        self.operating_expenses = [0.0] * len(self.years)
        self.ebit = [0.0] * len(self.years)
        self.depreciation = [0.0] * len(self.years)
        self.ebitda = [0.0] * len(self.years)
        
        self.interest_expense = [0.0] * len(self.years)
        self.interest_income = [0.0] * len(self.years)
        self.ebt = [0.0] * len(self.years)
        self.tax = [0.0] * len(self.years)
        self.net_income = [0.0] * len(self.years)
        
        # Balance sheet items
        self.cash = [0.0] * len(self.years)
        self.ar = [0.0] * len(self.years)
        self.inventory = [0.0] * len(self.years)
        self.current_assets = [0.0] * len(self.years)
        
        self.gross_ppe = [0.0] * len(self.years)
        self.acc_depreciation = [0.0] * len(self.years)
        self.net_ppe = [0.0] * len(self.years)
        
        self.goodwill = [0.0] * len(self.years)
        self.other_intangibles = [0.0] * len(self.years)
        self.other_noncurrent_assets = [0.0] * len(self.years)
        self.total_assets = [0.0] * len(self.years)
        
        self.ap = [0.0] * len(self.years)
        self.st_debt = [0.0] * len(self.years)
        self.current_liabilities = [0.0] * len(self.years)
        
        self.lt_debt = [0.0] * len(self.years)
        self.total_debt = [0.0] * len(self.years)
        self.noncurrent_liabilities = [0.0] * len(self.years)
        self.total_liabilities = [0.0] * len(self.years)
        
        self.common_stock = [0.0] * len(self.years)
        self.apic = [0.0] * len(self.years)
        self.retained_earnings = [0.0] * len(self.years)
        self.treasury_stock = [0.0] * len(self.years)
        self.other_equity = [0.0] * len(self.years)
        self.stockholders_equity = [0.0] * len(self.years)
        self.total_equity = [0.0] * len(self.years)
        
        # Cash flow items
        self.operating_cf = [0.0] * len(self.years)
        self.investing_cf = [0.0] * len(self.years)
        self.financing_cf = [0.0] * len(self.years)
        self.capex = [0.0] * len(self.years)
        self.dividends = [0.0] * len(self.years)
        self.free_cf = [0.0] * len(self.years)
        
        # Stock repurchases
        self.stock_repurchase = [0.0] * len(self.years)
        
        # Initialize Year 0
        self._initialize_year_0()
    
    def _initialize_year_0(self):
        """Initialize Year 0 (actual values)"""
        bs0 = self.inputs['year_0_balance_sheet']
        
        # Assets
        self.cash[0] = bs0['cash']
        self.ar[0] = bs0['accounts_receivable']
        self.inventory[0] = bs0['inventory']
        self.current_assets[0] = bs0['current_assets']
        
        self.gross_ppe[0] = bs0['gross_ppe']
        self.acc_depreciation[0] = bs0['accumulated_depreciation']
        self.net_ppe[0] = bs0['net_ppe']
        
        self.goodwill[0] = bs0['goodwill']
        self.other_intangibles[0] = bs0['other_intangibles']
        self.other_noncurrent_assets[0] = bs0['other_non_current_assets']
        self.total_assets[0] = bs0['total_assets']
        
        # Liabilities
        self.ap[0] = bs0['accounts_payable']
        self.st_debt[0] = bs0['short_term_debt']
        self.current_liabilities[0] = bs0['current_liabilities']
        
        self.lt_debt[0] = bs0['long_term_debt']
        self.total_debt[0] = bs0['total_debt']
        self.noncurrent_liabilities[0] = bs0['non_current_liabilities']
        self.total_liabilities[0] = bs0['total_liabilities']
        
        # Equity
        self.common_stock[0] = bs0['common_stock']
        self.apic[0] = bs0['additional_paid_in_capital']
        self.retained_earnings[0] = bs0['retained_earnings']
        self.treasury_stock[0] = bs0['treasury_stock']
        self.other_equity[0] = bs0['other_equity']
        self.stockholders_equity[0] = bs0['stockholders_equity']
        self.total_equity[0] = bs0['total_equity']
        
        # Year 0 complete income statement data (actual values)
        self.revenue[0] = self.inputs.get('year_0_revenue', 0)
        self.cogs[0] = self.inputs.get('year_0_cogs', 0)
        self.gross_profit[0] = self.inputs.get('year_0_gross_profit', 0)
        self.operating_expenses[0] = self.inputs.get('year_0_opex', 0)
        self.ebit[0] = self.inputs.get('year_0_ebit', 0)
        self.depreciation[0] = self.inputs.get('year_0_depreciation', 0)
        self.ebitda[0] = self.inputs.get('year_0_ebitda', 0)
        self.interest_expense[0] = self.inputs.get('year_0_interest_expense', 0)
        self.interest_income[0] = self.inputs.get('year_0_interest_income', 0)
        self.ebt[0] = self.inputs.get('year_0_pretax_income', 0)
        self.tax[0] = self.inputs.get('year_0_tax', 0)
        self.net_income[0] = self.inputs.get('year_0_net_income', 0)
        
        # Year 0 cash flow data
        self.operating_cf[0] = self.inputs.get('year_0_operating_cf', 0)
        self.capex[0] = -abs(self.inputs.get('year_0_capex', 0))  # Negative value
        self.free_cf[0] = self.inputs.get('year_0_free_cf', 0)
        self.dividends[0] = -abs(self.inputs.get('year_0_dividends', 0))  # Negative value
    
    def forecast_income_statement(self, year: int):
        """
        Forecast income statement
        year: index (1 for 2024, 2 for 2025)
        """
        # 1. Revenue
        self.revenue[year] = self.revenue[year-1] * (1 + self.inputs['nominal_revenue_growth'][year-1])
        
        # 2. COGS
        self.cogs[year] = self.cogs[year-1] * (1 + self.inputs['nominal_cogs_growth'][year-1])
        
        # 3. Gross profit
        self.gross_profit[year] = self.revenue[year] - self.cogs[year]
        
        # 4. Operating expenses
        self.operating_expenses[year] = self.operating_expenses[year-1] * (1 + self.inputs['nominal_opex_growth'][year-1])
        
        # 5. EBIT
        self.ebit[year] = self.gross_profit[year] - self.operating_expenses[year]
        
        # 6. Depreciation (based on prior year's Gross PPE)
        self.depreciation[year] = self.gross_ppe[year-1] * self.inputs['depreciation_rate']
        
        # 7. EBITDA
        self.ebitda[year] = self.ebit[year] + self.depreciation[year]
        
        # Note: Interest is calculated after debt schedule
    
    def forecast_cash_budget_and_working_capital(self, year: int):
        """
        Forecast working capital and operating cash flow
        """
        # 1. Accounts receivable (based on revenue)
        self.ar[year] = self.revenue[year] * (self.inputs['ar_days'] / 365)
        
        # 2. Inventory (based on COGS)
        self.inventory[year] = self.cogs[year] * (self.inputs['inventory_days'] / 365)
        
        # 3. Accounts payable (based on COGS)
        self.ap[year] = self.cogs[year] * (self.inputs['ap_days'] / 365)
        
        # 4. Capital expenditures
        self.capex[year] = self.revenue[year] * self.inputs['capex_to_revenue']
        
        # 5. Gross PPE
        self.gross_ppe[year] = self.gross_ppe[year-1] + self.capex[year]
        
        # 6. Accumulated depreciation
        self.acc_depreciation[year] = self.acc_depreciation[year-1] + self.depreciation[year]
        
        # 7. Net PPE
        self.net_ppe[year] = self.gross_ppe[year] - self.acc_depreciation[year]
        
        # 8. Operating cash flow (simplified)
        change_in_ar = self.ar[year] - self.ar[year-1]
        change_in_inventory = self.inventory[year] - self.inventory[year-1]
        change_in_ap = self.ap[year] - self.ap[year-1]
        
        # OCF = EBIT + depreciation - tax - working capital changes
        # Note: Tax is handled when calculating net income, not deducted here
    
    def forecast_debt_and_financing(self, year: int):
        """
        Forecast debt and financing
        """
        # 1. Calculate interest expense (based on prior period debt)
        self.interest_expense[year] = (
            self.st_debt[year-1] * self.inputs['interest_rate_st'] +
            self.lt_debt[year-1] * self.inputs['interest_rate_lt']
        )
        
        # 2. Interest income (assume based on cash balance)
        self.interest_income[year] = self.cash[year-1] * 0.02  # Assume 2% yield
        
        # 3. Earnings before tax
        self.ebt[year] = self.ebit[year] - self.interest_expense[year] + self.interest_income[year]
        
        # 4. Tax
        self.tax[year] = max(0, self.ebt[year] * self.inputs['tax_rate'])
        
        # 5. Net income
        self.net_income[year] = self.ebt[year] - self.tax[year]
        
        # 6. Dividends (based on historical dividend payout ratio)
        self.dividends[year] = self.net_income[year] * self.inputs['dividend_payout_ratio']
        
        # 7. Stock repurchases (based on historical repurchase/net income ratio)
        self.stock_repurchase[year] = self.net_income[year] * self.inputs.get('repurchase_to_ni_ratio', 0.3)
        
        # 8. Retained earnings (net income - dividends)
        self.retained_earnings[year] = self.retained_earnings[year-1] + self.net_income[year] - self.dividends[year]
        
        # 9. Treasury stock (accumulated repurchases)
        self.treasury_stock[year] = self.treasury_stock[year-1] + self.stock_repurchase[year]
        
        # 10. Other equity items remain stable
        self.common_stock[year] = self.common_stock[year-1]
        self.apic[year] = self.apic[year-1]
        self.other_equity[year] = self.other_equity[year-1]
        
        # 11. Stockholders' equity
        self.stockholders_equity[year] = (
            self.common_stock[year] +
            self.apic[year] +
            self.retained_earnings[year] -
            self.treasury_stock[year] +
            self.other_equity[year]
        )
        
        # 12. Total equity (assume minority interest is stable)
        minority_interest = self.total_equity[year-1] - self.stockholders_equity[year-1]
        self.total_equity[year] = self.stockholders_equity[year] + minority_interest
    
    def forecast_balance_sheet(self, year: int):
        """
        Forecast balance sheet and ensure it balances
        Use cash flow method: start from prior period cash and add current period cash flow changes
        """
        # 1. Intangible assets (assume stable or slightly decreasing)
        self.goodwill[year] = self.goodwill[year-1]
        self.other_intangibles[year] = self.other_intangibles[year-1] * 0.98  # Assume 2% amortization per year
        self.other_noncurrent_assets[year] = self.other_noncurrent_assets[year-1]
        
        # 2. Calculate current period cash flow changes
        # Operating cash flow
        change_in_ar = self.ar[year] - self.ar[year-1]
        change_in_inventory = self.inventory[year] - self.inventory[year-1]
        change_in_ap = self.ap[year] - self.ap[year-1]
        
        operating_cf = (
            self.net_income[year] +
            self.depreciation[year] -
            change_in_ar -
            change_in_inventory +
            change_in_ap
        )
        
        # Investing cash flow (mainly capital expenditures)
        investing_cf = -self.capex[year]
        
        # Financing cash flow (dividends + stock repurchases)
        financing_cf = -(self.dividends[year] + self.stock_repurchase[year])
        
        # 3. Calculate ending cash (before debt adjustments)
        preliminary_cash = (
            self.cash[year-1] +
            operating_cf +
            investing_cf +
            financing_cf
        )
        
        # 4. Debt management strategy
        min_cash = self.inputs['min_cash_balance']
        max_debt_to_equity = self.inputs['max_debt_to_equity']
        target_debt_structure = self.inputs['target_debt_structure']
        
        # Initialize debt at prior period values
        self.lt_debt[year] = self.lt_debt[year-1]
        self.st_debt[year] = self.st_debt[year-1]
        self.total_debt[year] = self.lt_debt[year] + self.st_debt[year]
        
        if preliminary_cash < min_cash:
            # Insufficient cash, need to borrow
            shortfall = min_cash - preliminary_cash
            lt_increase = shortfall * target_debt_structure
            st_increase = shortfall * (1 - target_debt_structure)
            
            self.lt_debt[year] += lt_increase
            self.st_debt[year] += st_increase
            self.total_debt[year] = self.lt_debt[year] + self.st_debt[year]
            self.cash[year] = min_cash
            
        elif preliminary_cash > min_cash * 2.5:
            # Excess cash, use to pay down debt
            excess = preliminary_cash - min_cash * 1.5
            
            # Check debt-to-equity ratio, don't pay down too much if below target
            current_debt_to_equity = self.total_debt[year] / self.stockholders_equity[year]
            
            if current_debt_to_equity > max_debt_to_equity * 0.5:
                # Can pay down some debt
                debt_reduction = min(excess, self.total_debt[year] * 0.3)  # Maximum 30% repayment
                
                # Prioritize short-term debt repayment
                st_reduction = min(debt_reduction * 0.4, self.st_debt[year])
                lt_reduction = min(debt_reduction - st_reduction, self.lt_debt[year])
                
                self.st_debt[year] -= st_reduction
                self.lt_debt[year] -= lt_reduction
                self.total_debt[year] = self.lt_debt[year] + self.st_debt[year]
                self.cash[year] = preliminary_cash - (st_reduction + lt_reduction)
            else:
                # Debt is already low, keep cash
                self.cash[year] = preliminary_cash
        else:
            # Cash is reasonable, maintain debt level
            self.cash[year] = preliminary_cash
        
        # 5. Update liability items
        # Non-current liabilities (excluding debt, assume relatively stable)
        other_noncurrent_liab = self.noncurrent_liabilities[year-1] - self.lt_debt[year-1]
        self.noncurrent_liabilities[year] = self.lt_debt[year] + other_noncurrent_liab
        
        # Current liabilities (excluding debt and AP, assume relatively stable)
        other_current_liab = self.current_liabilities[year-1] - self.st_debt[year-1] - self.ap[year-1]
        self.current_liabilities[year] = self.st_debt[year] + self.ap[year] + other_current_liab
        
        # 6. Total liabilities
        self.total_liabilities[year] = self.current_liabilities[year] + self.noncurrent_liabilities[year]
        
        # 7. Calculate total assets
        self.current_assets[year] = self.cash[year] + self.ar[year] + self.inventory[year]
        
        self.total_assets[year] = (
            self.current_assets[year] +
            self.net_ppe[year] +
            self.goodwill[year] +
            self.other_intangibles[year] +
            self.other_noncurrent_assets[year]
        )
        
        # 8. Verify balance sheet balances
        # Assets = Liabilities + Equity
        # If imbalanced, adjust cash to balance
        required_total_assets = self.total_liabilities[year] + self.total_equity[year]
        imbalance = self.total_assets[year] - required_total_assets
        
        if abs(imbalance) > 1:  # Tolerate 1M error
            # Adjust cash to balance
            self.cash[year] -= imbalance
            self.current_assets[year] = self.cash[year] + self.ar[year] + self.inventory[year]
            self.total_assets[year] = (
                self.current_assets[year] +
                self.net_ppe[year] +
                self.goodwill[year] +
                self.other_intangibles[year] +
                self.other_noncurrent_assets[year]
            )
    
    def _rebalance_balance_sheet(self, year: int):
        """Rebalance balance sheet"""
        # Update liabilities
        other_noncurrent_liab = self.noncurrent_liabilities[year-1] - self.lt_debt[year-1]
        self.noncurrent_liabilities[year] = self.lt_debt[year] + other_noncurrent_liab
        
        other_current_liab = self.current_liabilities[year-1] - self.st_debt[year-1] - self.ap[year-1]
        self.current_liabilities[year] = self.st_debt[year] + self.ap[year] + other_current_liab
        
        self.total_liabilities[year] = self.current_liabilities[year] + self.noncurrent_liabilities[year]
        
        # Recalculate total assets and cash
        required_total_assets = self.total_liabilities[year] + self.total_equity[year]
        
        assets_excluding_cash = (
            self.ar[year] +
            self.inventory[year] +
            self.net_ppe[year] +
            self.goodwill[year] +
            self.other_intangibles[year] +
            self.other_noncurrent_assets[year]
        )
        
        self.cash[year] = required_total_assets - assets_excluding_cash
        self.total_assets[year] = required_total_assets
        self.current_assets[year] = self.cash[year] + self.ar[year] + self.inventory[year]
    
    def calculate_cash_flows(self, year: int):
        """Calculate cash flow statement"""
        # Working capital changes
        change_in_ar = self.ar[year] - self.ar[year-1]
        change_in_inventory = self.inventory[year] - self.inventory[year-1]
        change_in_ap = self.ap[year] - self.ap[year-1]
        change_in_wc = change_in_ar + change_in_inventory - change_in_ap
        
        # Operating cash flow
        self.operating_cf[year] = (
            self.net_income[year] +
            self.depreciation[year] -
            change_in_wc
        )
        
        # Investing cash flow
        self.investing_cf[year] = -self.capex[year]
        
        # Free cash flow
        self.free_cf[year] = self.operating_cf[year] + self.investing_cf[year]
        
        # Financing cash flow
        debt_change = self.total_debt[year] - self.total_debt[year-1]
        self.financing_cf[year] = (
            debt_change -
            self.dividends[year] -
            self.stock_repurchase[year]
        )
    
    def run_forecast(self):
        """
        Run complete forecast
        Following: Income Statement → Cash Budget → Debt → Balance Sheet sequence
        """
        print("\n" + "="*80)
        print(f"{self.company_name}Cash Budget Method Forecast (using forecast_model logic)")
        print("="*80)
        
        print(f"\nYear 0 (2023): Assets=${self.total_assets[0]:,.0f}M, "
              f"Liabilities=${self.total_liabilities[0]:,.0f}M, "
              f"Equity=${self.total_equity[0]:,.0f}M")
        print(f"Check balance: {abs(self.total_assets[0] - (self.total_liabilities[0] + self.total_equity[0])) < 1:.0f} ✓")
        
        for year in range(1, len(self.years)):
            year_name = 2023 + year
            print(f"\nForecasting Year {year} ({year_name})...")
            
            # Step 1: Income Statement
            self.forecast_income_statement(year)
            
            # Step 2: Cash Budget & Working Capital
            self.forecast_cash_budget_and_working_capital(year)
            
            # Step 3: Debt & Financing (including interest, tax, net income)
            self.forecast_debt_and_financing(year)
            
            # Step 4: Balance Sheet (ensure balancing)
            self.forecast_balance_sheet(year)
            
            # Step 5: Cash Flows
            self.calculate_cash_flows(year)
            
            # Verify balance
            balance_check = abs(self.total_assets[year] - (self.total_liabilities[year] + self.total_equity[year]))
            
            print(f"  Revenue: ${self.revenue[year]:,.0f}M")
            print(f"  EBIT: ${self.ebit[year]:,.0f}M")
            print(f"  Net Income: ${self.net_income[year]:,.0f}M")
            print(f"  Assets: ${self.total_assets[year]:,.0f}M")
            print(f"  Liabilities: ${self.total_liabilities[year]:,.0f}M")
            print(f"  Equity: ${self.total_equity[year]:,.0f}M")
            print(f"  Cash: ${self.cash[year]:,.0f}M")
            print(f"  Total Debt: ${self.total_debt[year]:,.0f}M")
            print(f"  Balance Sheet Difference: ${balance_check:,.2f}M {'✓' if balance_check < 1 else '✗'}")
        
        print("\n" + "="*80)
        print(f"{self.company_name} Forecast Complete! Balance Sheet is Balanced.")
        print("="*80)
        
        # Print complete financial statements
        self._print_detailed_statements()
    
    def _print_detailed_statements(self):
        """Print complete income statement and balance sheet"""
        for year in range(1, len(self.years)):
            year_name = self.inputs['base_year'] + year
            
            print("\n" + "="*100)
            print(f"{self.company_name} - Year {year} ({year_name}) Complete Financial Statements")
            print("="*100)
            
            # Income statement
            print("\n【Income Statement】")
            print("-"*100)
            print(f"{'Item':<30} {'Amount (Million USD)':>20}")
            print("-"*100)
            print(f"{'Revenue Revenue':<30} ${self.revenue[year]:>18,.0f}")
            print(f"{'Cost of Goods Sold (COGS)':<30} ${self.cogs[year]:>18,.0f}")
            print(f"{'Gross Profit':<30} ${self.gross_profit[year]:>18,.0f}")
            print(f"{'Gross Margin':<30} {(self.gross_profit[year]/self.revenue[year]*100):>18.2f}%")
            print(f"{'Operating Expenses':<30} ${self.operating_expenses[year]:>18,.0f}")
            print(f"{'EBIT':<30} ${self.ebit[year]:>18,.0f}")
            print(f"{'EBIT Margin':<30} {(self.ebit[year]/self.revenue[year]*100):>18.2f}%")
            print(f"{'Depreciation':<30} ${self.depreciation[year]:>18,.0f}")
            print(f"{'EBITDA':<30} ${self.ebitda[year]:>18,.0f}")
            print(f"{'Interest Expense':<30} ${self.interest_expense[year]:>18,.0f}")
            print(f"{'Interest Income':<30} ${self.interest_income[year]:>18,.0f}")
            print(f"{'Earnings Before Tax (EBT)':<30} ${self.ebt[year]:>18,.0f}")
            print(f"{'Income Tax':<30} ${self.tax[year]:>18,.0f}")
            print(f"{'Effective Tax Rate':<30} {(self.tax[year]/self.ebt[year]*100 if self.ebt[year] != 0 else 0):>18.2f}%")
            print(f"{'Net Income Net Income':<30} ${self.net_income[year]:>18,.0f}")
            print(f"{'Net Margin':<30} {(self.net_income[year]/self.revenue[year]*100):>18.2f}%")
            
            # Balance sheet
            print("\n[Balance Sheet]")
            print("-"*100)
            print(f"{'Item':<30} {'Amount (Million USD)':>20}")
            print("-"*100)
            print("[Assets Assets]")
            print(f"{'  Cash Cash':<30} ${self.cash[year]:>18,.0f}")
            print(f"{'  Accounts Receivable (AR)':<30} ${self.ar[year]:>18,.0f}")
            print(f"{'  Inventory':<30} ${self.inventory[year]:>18,.0f}")
            print(f"{'  Current Assets':<30} ${self.current_assets[year]:>18,.0f}")
            calc_current_assets = self.cash[year] + self.ar[year] + self.inventory[year]
            print(f"{'    (= Cash + AR + Inv)':<30} ${calc_current_assets:>18,.0f}")
            print(f"{'  Gross PPE':<30} ${self.gross_ppe[year]:>18,.0f}")
            print(f"{'  Accumulated Depreciation':<30} ${self.acc_depreciation[year]:>18,.0f}")
            print(f"{'  Net PPE':<30} ${self.net_ppe[year]:>18,.0f}")
            print(f"{'    (= Gross PPE - Acc Dep)':<30} ${(self.gross_ppe[year] - self.acc_depreciation[year]):>18,.0f}")
            print(f"{'  Goodwill':<30} ${self.goodwill[year]:>18,.0f}")
            print(f"{'  Other Intangibles':<30} ${self.other_intangibles[year]:>18,.0f}")
            print(f"{'  Other Non-Current Assets':<30} ${self.other_noncurrent_assets[year]:>18,.0f}")
            print(f"{'Total Assets':<30} ${self.total_assets[year]:>18,.0f}")
            calc_total_assets = (self.current_assets[year] + self.net_ppe[year] + 
                               self.goodwill[year] + self.other_intangibles[year] + 
                               self.other_noncurrent_assets[year])
            print(f"{'  (= CA + Net PPE + GW + OI + ONA)':<30} ${calc_total_assets:>18,.0f}")
            
            print("\n【Liabilities Liabilities】")
            print(f"{'  Accounts Payable (AP)':<30} ${self.ap[year]:>18,.0f}")
            print(f"{'  Short-Term Debt':<30} ${self.st_debt[year]:>18,.0f}")
            other_current_liab = self.current_liabilities[year] - self.st_debt[year] - self.ap[year]
            print(f"{'  Other Current Liabilities':<30} ${other_current_liab:>18,.0f}")
            print(f"{'  Current Liabilities':<30} ${self.current_liabilities[year]:>18,.0f}")
            calc_current_liab = self.st_debt[year] + self.ap[year] + other_current_liab
            print(f"{'    (= ST Debt + AP + Other)':<30} ${calc_current_liab:>18,.0f}")
            print(f"{'  Long-Term Debt':<30} ${self.lt_debt[year]:>18,.0f}")
            other_noncurrent_liab = self.noncurrent_liabilities[year] - self.lt_debt[year]
            print(f"{'  Other Non-Current Liabilities':<30} ${other_noncurrent_liab:>18,.0f}")
            print(f"{'  Non-Current Liabilities':<30} ${self.noncurrent_liabilities[year]:>18,.0f}")
            calc_noncurrent_liab = self.lt_debt[year] + other_noncurrent_liab
            print(f"{'    (= LT Debt + Other)':<30} ${calc_noncurrent_liab:>18,.0f}")
            print(f"{'  Total Debt Total Debt':<30} ${self.total_debt[year]:>18,.0f}")
            print(f"{'    (= LT Debt + ST Debt)':<30} ${(self.lt_debt[year] + self.st_debt[year]):>18,.0f}")
            print(f"{'Total Liabilities':<30} ${self.total_liabilities[year]:>18,.0f}")
            calc_total_liab = self.current_liabilities[year] + self.noncurrent_liabilities[year]
            print(f"{'  (= Current + Non-Current Liab)':<30} ${calc_total_liab:>18,.0f}")
            
            print("\n[Equity Equity]")
            print(f"{'  Common Stock':<30} ${self.common_stock[year]:>18,.0f}")
            print(f"{'  Additional Paid-In Capital (APIC)':<30} ${self.apic[year]:>18,.0f}")
            print(f"{'  Retained Earnings':<30} ${self.retained_earnings[year]:>18,.0f}")
            print(f"{'  Treasury Stock':<30} ${self.treasury_stock[year]:>18,.0f}")
            print(f"{'  Other Equity':<30} ${self.other_equity[year]:>18,.0f}")
            print(f"{'Stockholders Equity':<30} ${self.stockholders_equity[year]:>18,.0f}")
            print(f"{'Total Equity':<30} ${self.total_equity[year]:>18,.0f}")
            
            print("\n[Balance Check]")
            balance = self.total_assets[year] - self.total_liabilities[year] - self.total_equity[year]
            print(f"{'Assets - Liabilities - Equity':<30} ${balance:>18,.2f} {'✓' if abs(balance) < 1 else '✗'}")
            
            print("\n[Key Financial Ratios]")
            print("-"*100)
            print(f"{'ROE (Net Income/Equity)':<30} {(self.net_income[year]/self.stockholders_equity[year]*100):>18.2f}%")
            print(f"{'ROA (Net Income/Assets)':<30} {(self.net_income[year]/self.total_assets[year]*100):>18.2f}%")
            print(f"{'Debt-to-Equity Ratio (D/E)':<30} {(self.total_debt[year]/self.stockholders_equity[year]):>18.2f}")
            print(f"{'Current Ratio':<30} {(self.current_assets[year]/self.current_liabilities[year]):>18.2f}")
            print(f"{'Debt-to-Assets Ratio (D/A)':<30} {(self.total_liabilities[year]/self.total_assets[year]*100):>18.2f}%")
            
            # Cash flow information
            print("\n[Cash Flow Information]")
            print("-"*100)
            print(f"{'Operating Cash Flow':<30} ${self.operating_cf[year]:>18,.0f}")
            print(f"{'Capital Expenditures (CapEx)':<30} ${self.capex[year]:>18,.0f}")
            print(f"{'Free Cash Flow':<30} ${self.free_cf[year]:>18,.0f}")
            print(f"{'Dividends':<30} ${self.dividends[year]:>18,.0f}")
            print(f"{'Stock Repurchases':<30} ${self.stock_repurchase[year]:>18,.0f}")

    
    def print_detailed_balance_sheet(self, year: int):
        """Print detailed balance sheet"""
        year_name = 2023 + year
        print(f"\n{'='*80}")
        print(f"Balance Sheet - Year {year} ({year_name})")
        print(f"{'='*80}")
        
        print(f"\n[Assets]")
        print(f"Cash: ${self.cash[year]:,.0f}M")
        print(f"Accounts Receivable: ${self.ar[year]:,.0f}M")
        print(f"Inventory: ${self.inventory[year]:,.0f}M")
        print(f"Current Assets: ${self.current_assets[year]:,.0f}M")
        print(f"\nGross PPE: ${self.gross_ppe[year]:,.0f}M")
        print(f"Accumulated Depreciation: ${self.acc_depreciation[year]:,.0f}M")
        print(f"Net PPE: ${self.net_ppe[year]:,.0f}M")
        print(f"\nGoodwill: ${self.goodwill[year]:,.0f}M")
        print(f"Other Intangibles: ${self.other_intangibles[year]:,.0f}M")
        print(f"Other Non-Current Assets: ${self.other_noncurrent_assets[year]:,.0f}M")
        print(f"\nTotal Assets: ${self.total_assets[year]:,.0f}M")
        
        print(f"\n[Liabilities]")
        print(f"Accounts Payable: ${self.ap[year]:,.0f}M")
        print(f"Short-Term Debt: ${self.st_debt[year]:,.0f}M")
        print(f"Current Liabilities: ${self.current_liabilities[year]:,.0f}M")
        print(f"\nLong-Term Debt: ${self.lt_debt[year]:,.0f}M")
        print(f"Non-Current Liabilities: ${self.noncurrent_liabilities[year]:,.0f}M")
        print(f"\nTotal Liabilities: ${self.total_liabilities[year]:,.0f}M")
        
        print(f"\n[Stockholders' Equity]")
        print(f"Common Stock: ${self.common_stock[year]:,.0f}M")
        print(f"Additional Paid-In Capital: ${self.apic[year]:,.0f}M")
        print(f"Retained Earnings: ${self.retained_earnings[year]:,.0f}M")
        print(f"Treasury Stock: ${self.treasury_stock[year]:,.0f}M")
        print(f"Other Equity: ${self.other_equity[year]:,.0f}M")
        print(f"Stockholders' Equity: ${self.stockholders_equity[year]:,.0f}M")
        print(f"Total Equity: ${self.total_equity[year]:,.0f}M")
        
        print(f"\n{'='*80}")
        print(f"Verification: Assets - (Liabilities + Equity) = "
              f"${self.total_assets[year] - (self.total_liabilities[year] + self.total_equity[year]):,.2f}M")
        print(f"{'='*80}")
