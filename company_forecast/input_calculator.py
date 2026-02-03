"""
Input Calculator Module

Calculates forecast input parameters from historical company data.
Derives all the inputs needed for forecasting without plugs.

Design Principle:
- Minimize fixed assumptions
- Calculate everything possible from historical data
- Allow company-specific overrides when needed
"""

import pandas as pd
import os
import sys
from typing import Dict, Optional, List
from .data_loader import DataLoader
from .config import ForecastConfig, ModelAssumptions

# Add configs directory to path
configs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs')
if configs_dir not in sys.path:
    sys.path.insert(0, os.path.dirname(configs_dir))

try:
    from configs.base_config import CompanyConfig, load_company_config
except ImportError:
    CompanyConfig = None
    load_company_config = None


class InputCalculator:
    """
    Calculates all forecast inputs from historical data.
    
    Key inputs derived:
    - Revenue growth rates
    - Cost structure (COGS %, SG&A %)
    - Depreciation rates
    - Tax rate
    - Working capital ratios (AR, Inventory, AP as % of revenue/COGS)
    - Interest rates (based on existing debt)
    - Payout ratio
    - Capital expenditure patterns
    """
    
    def __init__(self, data_loader: DataLoader, config: ForecastConfig, 
                 assumptions: ModelAssumptions = None,
                 company_config: 'CompanyConfig' = None):
        """
        Initialize input calculator
        
        Args:
            data_loader: DataLoader with historical data
            config: ForecastConfig object
            assumptions: ModelAssumptions (optional, uses defaults if not provided)
            company_config: CompanyConfig with company-specific settings (optional)
        """
        self.data = data_loader
        self.config = config
        self.assumptions = assumptions or ModelAssumptions()
        
        # Load company-specific config if available
        self.company_config = company_config
        if self.company_config is None and load_company_config is not None:
            # Try to load from configs directory
            company_name = getattr(data_loader, 'company_name', None)
            if company_name:
                try:
                    self.company_config = load_company_config(company_name)
                except:
                    pass
        
        # Calculated inputs
        self.inputs: Dict = {}
        
    def calculate_all_inputs(self) -> Dict:
        """
        Calculate all forecast inputs from historical data
        
        Returns:
            Dictionary containing all input parameters
        """
        print("\n  Calculating forecast inputs from historical data...")
        
        # Year 0 values (from latest historical year)
        self._calculate_year_0_values()
        
        # Growth and inflation assumptions
        self._calculate_growth_assumptions()
        
        # Cost structure
        self._calculate_cost_structure()
        
        # Working capital ratios
        self._calculate_working_capital_ratios()
        
        # Tax rate
        self._calculate_tax_rate()
        
        # Depreciation
        self._calculate_depreciation_inputs()
        
        # Interest rates
        self._calculate_interest_rates()
        
        # Financing parameters
        self._calculate_financing_params()
        
        # Payout ratio
        self._calculate_payout_ratio()
        
        # Capital expenditure
        self._calculate_capex_inputs()
        
        print("  ✓ Input calculation complete")
        
        return self.inputs
    
    def _calculate_year_0_values(self):
        """Extract Year 0 values from latest historical data"""
        # Income Statement - Year 0
        self.inputs['revenue_year_0'] = self.data.get_value('income', 'Total Revenue') or 0
        self.inputs['cogs_year_0'] = self.data.get_value('income', 'Cost Of Revenue') or 0
        self.inputs['gross_profit_year_0'] = self.data.get_value('income', 'Gross Profit') or 0
        self.inputs['operating_expense_year_0'] = self.data.get_value('income', 'Operating Expense') or 0
        self.inputs['sga_year_0'] = self.data.get_value('income', 'Selling General And Administration') or 0
        self.inputs['operating_income_year_0'] = self.data.get_value('income', 'Operating Income') or 0
        self.inputs['ebit_year_0'] = self.data.get_value('income', 'EBIT') or self.inputs['operating_income_year_0']
        self.inputs['interest_expense_year_0'] = self.data.get_value('income', 'Interest Expense') or 0
        self.inputs['pretax_income_year_0'] = self.data.get_value('income', 'Pretax Income') or 0
        self.inputs['tax_provision_year_0'] = self.data.get_value('income', 'Tax Provision') or 0
        self.inputs['net_income_year_0'] = self.data.get_value('income', 'Net Income') or 0
        self.inputs['depreciation_year_0'] = self.data.get_value('income', 'Reconciled Depreciation') or 0
        
        # Balance Sheet - Year 0
        self.inputs['cash_year_0'] = (self.data.get_value('balance', 'Cash Cash Equivalents And Short Term Investments') or 
                                      self.data.get_value('balance', 'Cash And Cash Equivalents') or 0)
        self.inputs['accounts_receivable_year_0'] = self.data.get_value('balance', 'Accounts Receivable') or 0
        self.inputs['inventory_year_0'] = self.data.get_value('balance', 'Inventory') or 0
        self.inputs['current_assets_year_0'] = self.data.get_value('balance', 'Current Assets') or 0
        self.inputs['net_ppe_year_0'] = self.data.get_value('balance', 'Net PPE') or 0
        self.inputs['gross_ppe_year_0'] = self.data.get_value('balance', 'Gross PPE') or 0
        self.inputs['accumulated_depreciation_year_0'] = abs(self.data.get_value('balance', 'Accumulated Depreciation') or 0)
        self.inputs['goodwill_year_0'] = self.data.get_value('balance', 'Goodwill') or 0
        self.inputs['intangible_assets_year_0'] = self.data.get_value('balance', 'Other Intangible Assets') or 0
        self.inputs['total_assets_year_0'] = self.data.get_value('balance', 'Total Assets') or 0
        
        self.inputs['accounts_payable_year_0'] = self.data.get_value('balance', 'Accounts Payable') or 0
        self.inputs['current_liabilities_year_0'] = self.data.get_value('balance', 'Current Liabilities') or 0
        self.inputs['short_term_debt_year_0'] = self.data.get_value('balance', 'Current Debt') or 0
        self.inputs['long_term_debt_year_0'] = self.data.get_value('balance', 'Long Term Debt') or 0
        self.inputs['total_debt_year_0'] = self.data.get_value('balance', 'Total Debt') or (
            self.inputs['short_term_debt_year_0'] + self.inputs['long_term_debt_year_0'])
        self.inputs['total_liabilities_year_0'] = self.data.get_value('balance', 'Total Liabilities Net Minority Interest') or 0
        self.inputs['total_equity_year_0'] = self.data.get_value('balance', 'Stockholders Equity') or 0
        self.inputs['retained_earnings_year_0'] = self.data.get_value('balance', 'Retained Earnings') or 0
        
        # Minority Interest (non-controlling interest in subsidiaries)
        self.inputs['minority_interest_year_0'] = self.data.get_value('balance', 'Minority Interest') or 0
        
        # Cash Flow - Year 0
        self.inputs['operating_cash_flow_year_0'] = self.data.get_value('cash', 'Operating Cash Flow') or 0
        self.inputs['capex_year_0'] = abs(self.data.get_value('cash', 'Capital Expenditure') or 
                                          self.data.get_value('cash', 'Capital Expenditure Reported') or 0)
        self.inputs['dividends_paid_year_0'] = abs(self.data.get_value('cash', 'Cash Dividends Paid') or 0)
        self.inputs['stock_repurchase_year_0'] = abs(self.data.get_value('cash', 'Common Stock Payments') or 0)
        
    def _calculate_growth_assumptions(self):
        """Calculate revenue growth and inflation assumptions"""
        # Get bounds from company config or use defaults
        min_growth = -0.10
        max_growth = 0.15
        default_growth = self.assumptions.default_revenue_growth
        default_inflation = self.assumptions.default_inflation_rate
        
        if self.company_config:
            min_growth = self.company_config.min_revenue_growth
            max_growth = self.company_config.max_revenue_growth
            default_growth = self.company_config.default_revenue_growth
            default_inflation = self.company_config.default_inflation_rate
        
        # Check for override first
        if self.company_config and self.company_config.revenue_growth_override is not None:
            self.inputs['revenue_growth_base'] = self.company_config.revenue_growth_override
        else:
            # Calculate historical revenue growth
            revenue_growth = self.data.calculate_growth_rate('income', 'Total Revenue', 3)
            
            if revenue_growth is not None:
                # Cap growth rate at company-specific bounds
                revenue_growth = max(min_growth, min(max_growth, revenue_growth))
                self.inputs['revenue_growth_base'] = revenue_growth
            else:
                self.inputs['revenue_growth_base'] = default_growth
        
        # Revenue growth by year (can vary slightly over forecast period)
        n_years = self.config.n_forecast_years
        self.inputs['revenue_growth'] = []
        base_growth = self.inputs['revenue_growth_base']
        
        for i in range(n_years):
            # Slight moderation of growth over time
            year_growth = base_growth * (1 - 0.05 * i)  # 5% decay per year
            self.inputs['revenue_growth'].append(year_growth)
        
        # Inflation rate assumption
        self.inputs['inflation_rate'] = [self.assumptions.default_inflation_rate] * n_years
        
    def _calculate_cost_structure(self):
        """Calculate cost structure ratios from historical data (using multi-year average)"""
        n_years = self.config.n_input_years
        
        # COGS as % of revenue - check override first
        if self.company_config and self.company_config.cogs_pct_override is not None:
            self.inputs['cogs_pct_revenue'] = self.company_config.cogs_pct_override
        else:
            cogs_pct = self.data.calculate_ratio_average('income', 'Cost Of Revenue', 'Total Revenue', n_years)
            if cogs_pct is not None:
                self.inputs['cogs_pct_revenue'] = cogs_pct
            else:
                revenue = self.inputs['revenue_year_0']
                cogs = self.inputs['cogs_year_0']
                self.inputs['cogs_pct_revenue'] = cogs / revenue if revenue > 0 and cogs else 0.60
        
        # Gross margin
        self.inputs['gross_margin'] = 1 - self.inputs['cogs_pct_revenue']
        
        # SG&A as % of revenue - check override first
        if self.company_config and self.company_config.sga_pct_override is not None:
            self.inputs['sga_pct_revenue'] = self.company_config.sga_pct_override
        else:
            sga_pct = self.data.calculate_ratio_average('income', 'Selling General And Administration', 'Total Revenue', n_years)
            if sga_pct is not None:
                self.inputs['sga_pct_revenue'] = sga_pct
            else:
                revenue = self.inputs['revenue_year_0']
                sga = self.inputs['sga_year_0']
                self.inputs['sga_pct_revenue'] = sga / revenue if revenue > 0 and sga else 0.20
        
        # Operating margin (multi-year average)
        operating_margin = self.data.calculate_ratio_average('income', 'Operating Income', 'Total Revenue', n_years)
        if operating_margin is not None:
            self.inputs['operating_margin'] = operating_margin
        else:
            self.inputs['operating_margin'] = 0.15
    
    def _calculate_working_capital_ratios(self):
        """Calculate working capital ratios from historical data (using multi-year average)"""
        n_years = self.config.n_input_years
        revenue = self.inputs['revenue_year_0']
        cogs = self.inputs['cogs_year_0']
        
        # Accounts Receivable as % of revenue (multi-year average)
        ar_pct = self.data.calculate_cross_statement_ratio(
            'balance', 'Accounts Receivable', 'income', 'Total Revenue', n_years)
        if ar_pct is not None and ar_pct > 0:
            self.inputs['ar_pct_revenue'] = ar_pct
            self.inputs['days_sales_outstanding'] = ar_pct * 365
        else:
            ar = self.inputs['accounts_receivable_year_0']
            if revenue > 0 and ar > 0:
                self.inputs['ar_pct_revenue'] = ar / revenue
                self.inputs['days_sales_outstanding'] = (ar / revenue) * 365
            else:
                self.inputs['ar_pct_revenue'] = self.assumptions.default_ar_pct
                self.inputs['days_sales_outstanding'] = self.assumptions.default_ar_pct * 365
        
        # Inventory as % of COGS (multi-year average)
        inv_pct = self.data.calculate_cross_statement_ratio(
            'balance', 'Inventory', 'income', 'Cost Of Revenue', n_years)
        if inv_pct is not None and inv_pct > 0:
            self.inputs['inventory_pct_cogs'] = inv_pct
            self.inputs['days_inventory'] = inv_pct * 365
        else:
            inventory = self.inputs['inventory_year_0']
            if cogs > 0 and inventory > 0:
                self.inputs['inventory_pct_cogs'] = inventory / cogs
                self.inputs['days_inventory'] = (inventory / cogs) * 365
            else:
                self.inputs['inventory_pct_cogs'] = self.assumptions.default_inventory_pct
                self.inputs['days_inventory'] = self.assumptions.default_inventory_pct * 365
        
        # Accounts Payable as % of COGS (multi-year average)
        ap_pct = self.data.calculate_cross_statement_ratio(
            'balance', 'Accounts Payable', 'income', 'Cost Of Revenue', n_years)
        if ap_pct is not None and ap_pct > 0:
            self.inputs['ap_pct_cogs'] = ap_pct
            self.inputs['days_payable'] = ap_pct * 365
        else:
            ap = self.inputs['accounts_payable_year_0']
            if cogs > 0 and ap > 0:
                self.inputs['ap_pct_cogs'] = ap / cogs
                self.inputs['days_payable'] = (ap / cogs) * 365
            else:
                self.inputs['ap_pct_cogs'] = self.assumptions.default_ap_pct
                self.inputs['days_payable'] = self.assumptions.default_ap_pct * 365
        
        # Minimum cash as % of revenue (multi-year average)
        cash_pct = self.data.calculate_cross_statement_ratio(
            'balance', 'Cash And Cash Equivalents', 'income', 'Total Revenue', n_years)
        if cash_pct is not None and cash_pct > 0:
            self.inputs['min_cash_pct_revenue'] = cash_pct
        else:
            cash = self.inputs['cash_year_0']
            if revenue > 0 and cash > 0:
                self.inputs['min_cash_pct_revenue'] = cash / revenue
            else:
                self.inputs['min_cash_pct_revenue'] = self.assumptions.min_cash_pct_revenue
    
    def _calculate_tax_rate(self):
        """Calculate effective tax rate from historical data (multi-year average)"""
        # Get bounds and defaults from company config
        min_tax = 0.10
        max_tax = 0.35
        default_tax = self.assumptions.default_tax_rate
        
        if self.company_config:
            min_tax = self.company_config.min_tax_rate
            max_tax = self.company_config.max_tax_rate
            default_tax = self.company_config.default_tax_rate
        
        # Check override first
        if self.company_config and self.company_config.tax_rate_override is not None:
            self.inputs['tax_rate'] = self.company_config.tax_rate_override
            return
        
        n_years = self.config.n_input_years
        
        # Try multi-year average first
        tax_rate = self.data.calculate_ratio_average('income', 'Tax Provision', 'Pretax Income', n_years)
        
        if tax_rate is not None and 0 < tax_rate < 1:
            # Cap at company-specific bounds
            self.inputs['tax_rate'] = max(min_tax, min(max_tax, tax_rate))
        else:
            # Fallback to Year 0
            pretax_income = self.inputs['pretax_income_year_0']
            tax_provision = self.inputs['tax_provision_year_0']
            
            if pretax_income > 0 and tax_provision > 0:
                effective_rate = tax_provision / pretax_income
                self.inputs['tax_rate'] = max(min_tax, min(max_tax, effective_rate))
            else:
                self.inputs['tax_rate'] = default_tax
    
    def _calculate_depreciation_inputs(self):
        """Calculate depreciation-related inputs"""
        # Get bounds from company config
        min_depr_years = 5.0
        max_depr_years = 20.0
        default_depr_years = self.assumptions.default_depreciation_years
        
        if self.company_config:
            min_depr_years = self.company_config.min_depreciation_years
            max_depr_years = self.company_config.max_depreciation_years
            default_depr_years = self.company_config.default_depreciation_years
        
        net_ppe = self.inputs['net_ppe_year_0']
        gross_ppe = self.inputs['gross_ppe_year_0']
        depreciation = self.inputs['depreciation_year_0']
        
        # Estimate useful life from accumulated depreciation / depreciation expense
        accumulated_depr = self.inputs['accumulated_depreciation_year_0']
        if depreciation > 0:
            # Rough estimate: average age = accumulated / annual depreciation
            # Useful life ≈ gross PPE / depreciation
            self.inputs['depreciation_years'] = gross_ppe / depreciation if gross_ppe > 0 else default_depr_years
            self.inputs['depreciation_years'] = max(min_depr_years, min(max_depr_years, self.inputs['depreciation_years']))
        else:
            self.inputs['depreciation_years'] = default_depr_years
        
        # Depreciation rate (depreciation / average net PPE)
        if net_ppe > 0:
            self.inputs['depreciation_rate'] = depreciation / net_ppe
        else:
            self.inputs['depreciation_rate'] = 1 / self.inputs['depreciation_years']
    
    def _calculate_interest_rates(self):
        """Calculate interest rates from historical data"""
        # Get default parameters from company config
        default_inflation = self.assumptions.default_inflation_rate
        
        if self.company_config:
            default_inflation = self.company_config.default_inflation_rate
        
        interest_expense = self.inputs['interest_expense_year_0']
        total_debt = self.inputs['total_debt_year_0']
        
        # Check for cost of debt override
        if self.company_config and self.company_config.cost_of_debt_override is not None:
            self.inputs['cost_of_debt'] = self.company_config.cost_of_debt_override
        else:
            # Calculate implied cost of debt from historical data
            if total_debt > 0 and interest_expense > 0:
                implied_cost = interest_expense / total_debt
                self.inputs['cost_of_debt'] = max(0.03, min(0.15, implied_cost))
            else:
                self.inputs['cost_of_debt'] = 0.05  # Default 5%
        
        # Calculate return on short-term investments from historical data
        # Interest Income / Cash & Short-term Investments
        interest_income = self.data.get_value('income', 'Interest Income') or \
                         self.data.get_value('income', 'Interest Income Non Operating') or 0
        cash_st_inv = self.inputs['cash_year_0']
        
        if cash_st_inv > 0 and interest_income > 0:
            # Calculate implied return on ST investments
            implied_return = interest_income / cash_st_inv
            self.inputs['return_st_investment'] = max(0.01, min(0.08, implied_return))
        else:
            # Default: slightly below cost of debt (lower risk)
            self.inputs['return_st_investment'] = max(0.01, self.inputs['cost_of_debt'] - 0.01)
        
        # Store these as arrays for each forecast year
        n_years = self.config.n_forecast_years
        self.inputs['cost_of_debt_by_year'] = [self.inputs['cost_of_debt']] * n_years
        self.inputs['return_st_investment_by_year'] = [self.inputs['return_st_investment']] * n_years
    
    def _calculate_financing_params(self):
        """Calculate financing parameters from company config"""
        # Get from company config if available
        if self.company_config:
            self.inputs['pct_financing_with_debt'] = self.company_config.pct_financing_with_debt
            self.inputs['st_loan_years'] = self.company_config.st_loan_years
            self.inputs['lt_loan_years'] = self.company_config.lt_loan_years
        else:
            # Fall back to defaults
            self.inputs['pct_financing_with_debt'] = self.assumptions.pct_financing_with_debt
            self.inputs['st_loan_years'] = self.assumptions.st_loan_years
            self.inputs['lt_loan_years'] = self.assumptions.lt_loan_years
    
    def _calculate_payout_ratio(self):
        """Calculate dividend payout ratio from historical data (multi-year average)"""
        # Get default from company config
        default_payout = self.assumptions.default_payout_ratio
        if self.company_config:
            default_payout = self.company_config.default_payout_ratio
        
        # Check override first
        if self.company_config and self.company_config.payout_ratio_override is not None:
            self.inputs['payout_ratio'] = self.company_config.payout_ratio_override
            return
        
        n_years = self.config.n_input_years
        
        # Try multi-year average: dividends paid / net income
        payout = self.data.calculate_cross_statement_ratio(
            'cash', 'Cash Dividends Paid', 'income', 'Net Income', n_years)
        
        if payout is not None:
            # Dividends paid is negative in cash flow, so take absolute value
            payout = abs(payout)
            self.inputs['payout_ratio'] = max(0, min(1.0, payout))
        else:
            # Fallback to Year 0
            net_income = self.inputs['net_income_year_0']
            dividends = self.inputs['dividends_paid_year_0']
            
            if net_income > 0 and dividends > 0:
                payout = dividends / net_income
                self.inputs['payout_ratio'] = max(0, min(1.0, payout))
            else:
                self.inputs['payout_ratio'] = default_payout
    
    def _calculate_capex_inputs(self):
        """Calculate capital expenditure inputs (multi-year average)"""
        n_years = self.config.n_input_years
        
        # Check override first
        if self.company_config and self.company_config.capex_pct_override is not None:
            self.inputs['capex_pct_revenue'] = self.company_config.capex_pct_override
        else:
            # CapEx as % of revenue (multi-year average)
            capex_pct = self.data.calculate_cross_statement_ratio(
                'cash', 'Capital Expenditure', 'income', 'Total Revenue', n_years)
            
            if capex_pct is not None:
                # CapEx is negative in cash flow, so take absolute value
                self.inputs['capex_pct_revenue'] = abs(capex_pct)
            else:
                capex = self.inputs['capex_year_0']
                revenue = self.inputs['revenue_year_0']
                if revenue > 0 and capex > 0:
                    self.inputs['capex_pct_revenue'] = capex / revenue
                else:
                    self.inputs['capex_pct_revenue'] = 0.04  # Default 4%
        
        # CapEx as % of depreciation (maintenance vs growth)
        depreciation = self.inputs['depreciation_year_0']
        capex = self.inputs['capex_year_0']
        if depreciation > 0 and capex > 0:
            self.inputs['capex_to_depreciation'] = capex / depreciation
        else:
            self.inputs['capex_to_depreciation'] = 1.2  # Slightly above maintenance
    
    def get_summary(self) -> str:
        """Return a formatted summary of calculated inputs"""
        lines = [
            f"\n{'='*60}",
            f"CALCULATED INPUTS SUMMARY",
            f"{'='*60}",
            f"\nYear 0 Values:",
            f"  Revenue: ${self.inputs.get('revenue_year_0', 0):,.0f}",
            f"  COGS: ${self.inputs.get('cogs_year_0', 0):,.0f}",
            f"  Operating Income: ${self.inputs.get('operating_income_year_0', 0):,.0f}",
            f"  Net Income: ${self.inputs.get('net_income_year_0', 0):,.0f}",
            f"  Total Assets: ${self.inputs.get('total_assets_year_0', 0):,.0f}",
            f"  Total Equity: ${self.inputs.get('total_equity_year_0', 0):,.0f}",
            f"\nGrowth Assumptions:",
            f"  Revenue Growth: {self.inputs.get('revenue_growth_base', 0)*100:.1f}%",
            f"\nCost Structure:",
            f"  COGS % of Revenue: {self.inputs.get('cogs_pct_revenue', 0)*100:.1f}%",
            f"  Gross Margin: {self.inputs.get('gross_margin', 0)*100:.1f}%",
            f"  SG&A % of Revenue: {self.inputs.get('sga_pct_revenue', 0)*100:.1f}%",
            f"\nWorking Capital:",
            f"  Days Sales Outstanding: {self.inputs.get('days_sales_outstanding', 0):.0f} days",
            f"  Days Inventory: {self.inputs.get('days_inventory', 0):.0f} days",
            f"  Days Payable: {self.inputs.get('days_payable', 0):.0f} days",
            f"\nOther Assumptions:",
            f"  Tax Rate: {self.inputs.get('tax_rate', 0)*100:.1f}%",
            f"  Payout Ratio: {self.inputs.get('payout_ratio', 0)*100:.1f}%",
            f"  Cost of Debt: {self.inputs.get('cost_of_debt', 0)*100:.1f}%",
            f"  Depreciation Years: {self.inputs.get('depreciation_years', 0):.1f}",
            f"{'='*60}",
        ]
        return '\n'.join(lines)
