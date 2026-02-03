"""
Intermediate calculations module.
Computes all intermediate values needed for cash budget and financial statements.
"""

from typing import List, Dict
from .config import ForecastConfig


class IntermediateCalculations:
    """
    Handles all intermediate calculations including:
    - Revenue forecasts
    - Cost of goods sold
    - Operating expenses (SG&A)
    - Depreciation schedules
    - Working capital changes
    - Interest rate calculations
    """
    
    def __init__(self, inputs: Dict, config: ForecastConfig):
        """
        Initialize intermediate calculations
        
        Args:
            inputs: Dictionary of calculated inputs from InputCalculator
            config: ForecastConfig object
        """
        self.inputs = inputs
        self.config = config
        self.n_years = config.n_forecast_years
        
        # Revenue and Sales
        self.revenue = [inputs['revenue_year_0']]  # Year 0 is historical
        
        # Cost of Goods Sold
        self.cogs = [inputs['cogs_year_0']]
        
        # Gross Profit
        self.gross_profit = [inputs['gross_profit_year_0']]
        
        # Operating Expenses (SG&A)
        self.sga_expenses = [inputs['sga_year_0']]
        
        # Operating Income (EBIT)
        self.operating_income = [inputs['operating_income_year_0']]
        
        # Depreciation
        self.depreciation = [inputs['depreciation_year_0']]
        self.cumulated_depreciation = [inputs['accumulated_depreciation_year_0']]
        
        # Fixed Assets
        self.net_ppe = [inputs['net_ppe_year_0']]
        self.gross_ppe = [inputs['gross_ppe_year_0']]
        self.capex = [inputs['capex_year_0']]
        
        # Working Capital Items
        self.accounts_receivable = [inputs['accounts_receivable_year_0']]
        self.inventory = [inputs['inventory_year_0']]
        self.accounts_payable = [inputs['accounts_payable_year_0']]
        
        # Cash Requirements
        self.min_cash_required = [inputs['cash_year_0']]
        
        # Interest Rates (by year)
        self.cost_of_debt = inputs.get('cost_of_debt_by_year', [inputs['cost_of_debt']] * self.n_years)
        self.return_st_investment = inputs.get('return_st_investment_by_year', 
                                                [inputs['return_st_investment']] * self.n_years)
        
        # Cash Flow Components (will be calculated)
        self.change_in_ar = []
        self.change_in_inventory = []
        self.change_in_ap = []
        self.change_in_working_capital = []
        
        # Other intangibles (keep constant from Year 0)
        self.goodwill = [inputs['goodwill_year_0']]
        self.intangible_assets = [inputs['intangible_assets_year_0']]
        
    def calculate_all(self):
        """Execute all intermediate calculations in proper order"""
        print("  Calculating intermediate values...")
        
        self._calculate_revenue_forecast()
        self._calculate_cogs()
        self._calculate_sga_expenses()
        self._calculate_capex_and_ppe_and_depreciation()
        self._calculate_working_capital()
        self._calculate_min_cash()
        
        print("  ✓ Intermediate calculations complete")
    
    def _calculate_revenue_forecast(self):
        """Forecast revenue for each year"""
        for i in range(self.n_years):
            growth_rate = self.inputs['revenue_growth'][i]
            prev_revenue = self.revenue[i]
            new_revenue = prev_revenue * (1 + growth_rate)
            self.revenue.append(new_revenue)
    
    def _calculate_cogs(self):
        """Calculate COGS for each forecast year"""
        cogs_pct = self.inputs['cogs_pct_revenue']
        
        for i in range(self.n_years):
            revenue = self.revenue[i + 1]  # i+1 because revenue[0] is Year 0
            new_cogs = revenue * cogs_pct
            self.cogs.append(new_cogs)
            
            # Gross profit
            gross_profit = revenue - new_cogs
            self.gross_profit.append(gross_profit)
    
    def _calculate_sga_expenses(self):
        """Calculate SG&A expenses for each forecast year"""
        sga_pct = self.inputs['sga_pct_revenue']
        
        for i in range(self.n_years):
            revenue = self.revenue[i + 1]
            new_sga = revenue * sga_pct
            self.sga_expenses.append(new_sga)
    
    def _calculate_capex_and_ppe_and_depreciation(self):
        """Calculate CapEx, PPE, and Depreciation for each forecast year"""
        capex_pct_revenue = self.inputs['capex_pct_revenue']
        depr_rate = self.inputs['depreciation_rate']
        
        for year in range(1, self.n_years + 1):
            # CapEx based on revenue
            revenue = self.revenue[year]
            new_capex = revenue * capex_pct_revenue
            self.capex.append(new_capex)
            
            # Gross PPE = previous + CapEx
            gross_ppe = self.gross_ppe[year - 1] + new_capex
            self.gross_ppe.append(gross_ppe)
            
            # Depreciation based on beginning-of-year Net PPE
            net_ppe_begin = self.net_ppe[year - 1]
            new_depr = net_ppe_begin * depr_rate
            self.depreciation.append(new_depr)
            
            # Cumulated depreciation
            cum_depr = self.cumulated_depreciation[year - 1] + new_depr
            self.cumulated_depreciation.append(cum_depr)
            
            # Net PPE = Previous Net PPE + CapEx - Depreciation
            net_ppe = net_ppe_begin + new_capex - new_depr
            self.net_ppe.append(net_ppe)
            
            # Keep intangibles constant (simplified assumption)
            self.goodwill.append(self.goodwill[0])
            self.intangible_assets.append(self.intangible_assets[0])
    
    def _calculate_working_capital(self):
        """Calculate working capital items for each forecast year"""
        ar_pct = self.inputs['ar_pct_revenue']
        inv_pct_cogs = self.inputs['inventory_pct_cogs']
        ap_pct_cogs = self.inputs['ap_pct_cogs']
        
        for year in range(1, self.n_years + 1):
            i = year - 1  # Index for forecast year (0-based)
            
            # Accounts Receivable = AR % × Revenue
            revenue = self.revenue[year]
            new_ar = revenue * ar_pct
            self.accounts_receivable.append(new_ar)
            
            # Inventory = Inventory % × COGS
            cogs = self.cogs[year]
            new_inventory = cogs * inv_pct_cogs
            self.inventory.append(new_inventory)
            
            # Accounts Payable = AP % × COGS
            new_ap = cogs * ap_pct_cogs
            self.accounts_payable.append(new_ap)
            
            # Changes in working capital
            change_ar = new_ar - self.accounts_receivable[year - 1]
            change_inv = new_inventory - self.inventory[year - 1]
            change_ap = new_ap - self.accounts_payable[year - 1]
            
            self.change_in_ar.append(change_ar)
            self.change_in_inventory.append(change_inv)
            self.change_in_ap.append(change_ap)
            
            # Change in working capital (increase in WC uses cash)
            # WC = AR + Inventory - AP
            # Change in WC = ΔAR + ΔInventory - ΔAP
            change_wc = change_ar + change_inv - change_ap
            self.change_in_working_capital.append(change_wc)
    
    def _calculate_min_cash(self):
        """Calculate minimum cash required for each year"""
        min_cash_pct = self.inputs['min_cash_pct_revenue']
        
        for year in range(1, self.n_years + 1):
            revenue = self.revenue[year]
            min_cash = revenue * min_cash_pct
            self.min_cash_required.append(min_cash)
    
    def calculate_operating_income(self, year: int) -> float:
        """
        Calculate operating income for a specific year
        (Called after depreciation is calculated)
        
        Args:
            year: Year number (1-4)
            
        Returns:
            Operating income
        """
        gross_profit = self.gross_profit[year]
        sga = self.sga_expenses[year]
        depreciation = self.depreciation[year]
        
        operating_income = gross_profit - sga - depreciation
        
        if year >= len(self.operating_income):
            self.operating_income.append(operating_income)
        else:
            self.operating_income[year] = operating_income
            
        return operating_income
