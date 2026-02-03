"""
Balance Sheet module for company forecasting.
Compiles balance sheet from all other calculations.
"""

from typing import Dict, List
from .config import ForecastConfig


class BalanceSheet:
    """
    Handles balance sheet compilation including:
    - Assets (current and non-current)
    - Liabilities (current and non-current)
    - Stockholders' Equity
    
    Balance sheet identity: Assets = Liabilities + Equity
    Using NO PLUG approach - all items are calculated from other modules.
    
    Key insight: Equity changes through:
    1. Net Income (retained)
    2. Dividends (reduces RE)
    3. New equity issued
    4. Stock repurchases
    """
    
    def __init__(self, inputs: Dict, config: ForecastConfig):
        """
        Initialize balance sheet
        
        Args:
            inputs: Dictionary of calculated inputs
            config: ForecastConfig object
        """
        self.inputs = inputs
        self.config = config
        self.n_years = config.n_forecast_years
        
        # Current Assets
        self.cash = [inputs['cash_year_0']]
        self.accounts_receivable = [inputs['accounts_receivable_year_0']]
        self.inventory = [inputs['inventory_year_0']]
        self.st_investment = [0]
        self.other_current_assets = [max(0, inputs['current_assets_year_0'] - 
                                     inputs['cash_year_0'] - 
                                     inputs['accounts_receivable_year_0'] - 
                                     inputs['inventory_year_0'])]
        self.current_assets = [inputs['current_assets_year_0']]
        
        # Non-Current Assets
        self.net_ppe = [inputs['net_ppe_year_0']]
        self.goodwill = [inputs['goodwill_year_0']]
        self.intangible_assets = [inputs['intangible_assets_year_0']]
        self.other_non_current_assets = [max(0, inputs['total_assets_year_0'] - 
                                         inputs['current_assets_year_0'] -
                                         inputs['net_ppe_year_0'] -
                                         inputs['goodwill_year_0'] -
                                         inputs['intangible_assets_year_0'])]
        self.total_non_current_assets = [inputs['total_assets_year_0'] - inputs['current_assets_year_0']]
        self.total_assets = [inputs['total_assets_year_0']]
        
        # Current Liabilities
        self.accounts_payable = [inputs['accounts_payable_year_0']]
        self.short_term_debt = [inputs['short_term_debt_year_0']]
        self.other_current_liabilities = [max(0, inputs['current_liabilities_year_0'] -
                                          inputs['accounts_payable_year_0'] -
                                          inputs['short_term_debt_year_0'])]
        self.current_liabilities = [inputs['current_liabilities_year_0']]
        
        # Non-Current Liabilities
        self.long_term_debt = [inputs['long_term_debt_year_0']]
        self.other_non_current_liabilities = [max(0, inputs['total_liabilities_year_0'] -
                                              inputs['current_liabilities_year_0'] -
                                              inputs['long_term_debt_year_0'])]
        self.total_non_current_liabilities = [inputs['total_liabilities_year_0'] - 
                                              inputs['current_liabilities_year_0']]
        self.total_liabilities = [inputs['total_liabilities_year_0']]
        
        # Stockholders' Equity - keep it simple
        # Total equity = Total Assets - Total Liabilities (accounting identity)
        self.retained_earnings = [inputs['retained_earnings_year_0']]
        self.other_equity = [inputs['total_equity_year_0'] - inputs['retained_earnings_year_0']]
        self.total_equity = [inputs['total_equity_year_0']]
        
        # Minority Interest (non-controlling interest) - kept constant over forecast
        self.minority_interest = [inputs.get('minority_interest_year_0', 0)]
        
        # Total Liabilities & Equity (including minority interest)
        self.total_liabilities_equity = [inputs['total_liabilities_year_0'] + inputs['total_equity_year_0'] + self.minority_interest[0]]
        
        # Check (should be zero if balanced)
        self.balance_check = [self.total_assets[0] - self.total_liabilities_equity[0]]
    
    def calculate_year(self, year: int, intermediate, cash_budget, debt_schedule, income_statement):
        """
        Calculate balance sheet for a specific year
        
        Uses the accounting equation: Assets = Liabilities + Equity
        
        The balance sheet should balance because:
        - Change in Assets = Operating CF + Investing CF
        - Change in Liabilities = Net borrowing - Debt repayments
        - Change in Equity = Net Income - Dividends + New Equity - Repurchases
        
        And: Operating CF + Investing CF + Financing CF = Change in Cash
        
        Args:
            year: Year number (1-4)
            intermediate: IntermediateCalculations object
            cash_budget: CashBudget object
            debt_schedule: DebtSchedule object
            income_statement: IncomeStatement object
        """
        i = year - 1  # 0-based index
        
        # ===== CURRENT ASSETS =====
        # Cash = ending cash from cash budget
        cash = cash_budget.cumulated_ncb[year]
        self.cash.append(cash)
        
        # Accounts Receivable from intermediate
        ar = intermediate.accounts_receivable[year]
        self.accounts_receivable.append(ar)
        
        # Inventory from intermediate
        inventory = intermediate.inventory[year]
        self.inventory.append(inventory)
        
        # ST Investment from cash budget
        st_inv = cash_budget.st_investment[year]
        self.st_investment.append(st_inv)
        
        # Other current assets (keep constant)
        other_ca = self.other_current_assets[0]
        self.other_current_assets.append(other_ca)
        
        current_assets = cash + ar + inventory + st_inv + other_ca
        self.current_assets.append(current_assets)
        
        # ===== NON-CURRENT ASSETS =====
        # Net PPE from intermediate
        net_ppe = intermediate.net_ppe[year]
        self.net_ppe.append(net_ppe)
        
        # Goodwill and intangibles (keep constant)
        goodwill = intermediate.goodwill[year]
        intangibles = intermediate.intangible_assets[year]
        self.goodwill.append(goodwill)
        self.intangible_assets.append(intangibles)
        
        # Other non-current assets (keep constant)
        other_nca = self.other_non_current_assets[0]
        self.other_non_current_assets.append(other_nca)
        
        total_nca = net_ppe + goodwill + intangibles + other_nca
        self.total_non_current_assets.append(total_nca)
        
        total_assets = current_assets + total_nca
        self.total_assets.append(total_assets)
        
        # ===== CURRENT LIABILITIES =====
        # Accounts Payable from intermediate
        ap = intermediate.accounts_payable[year]
        self.accounts_payable.append(ap)
        
        # Short-term debt from debt schedule
        st_debt = debt_schedule.st_ending_balance[year]
        self.short_term_debt.append(st_debt)
        
        # Other current liabilities (keep constant)
        other_cl = self.other_current_liabilities[0]
        self.other_current_liabilities.append(other_cl)
        
        current_liabilities = ap + st_debt + other_cl
        self.current_liabilities.append(current_liabilities)
        
        # ===== NON-CURRENT LIABILITIES =====
        # Long-term debt from debt schedule
        lt_debt = debt_schedule.lt_ending_balance[year]
        self.long_term_debt.append(lt_debt)
        
        # Other non-current liabilities (keep constant)
        other_ncl = self.other_non_current_liabilities[0]
        self.other_non_current_liabilities.append(other_ncl)
        
        total_ncl = lt_debt + other_ncl
        self.total_non_current_liabilities.append(total_ncl)
        
        total_liabilities = current_liabilities + total_ncl
        self.total_liabilities.append(total_liabilities)
        
        # ===== STOCKHOLDERS' EQUITY =====
        # Calculate equity from its components
        # Other Equity changes with new equity issued and stock repurchases
                
        # First, calculate what retained earnings should be based on income statement
        # Retained earnings: Previous RE + Net Income + ST Investment Return - Dividends
        # Note: ST Investment Return is interest income not captured in Income Statement
        prev_re = self.retained_earnings[year - 1]
        net_income = income_statement.net_income[year]
        dividends = cash_budget.dividends_paid[year]
        st_investment_return = cash_budget.st_investment_return[year]  # Interest income from ST investments
        
        # Retained earnings change (including ST investment interest income)
        retained_earnings = prev_re + net_income + st_investment_return - dividends
        self.retained_earnings.append(retained_earnings)
        
        # Other equity: adjust for new equity and repurchases
        prev_other_equity = self.other_equity[year - 1]
        new_equity = cash_budget.equity_invested[year]
        repurchases = cash_budget.stock_repurchase[year]
        
        other_equity = prev_other_equity + new_equity - repurchases
        self.other_equity.append(other_equity)
        
        # Total equity from components
        total_equity = retained_earnings + other_equity
        self.total_equity.append(total_equity)
        
        # Minority Interest (keep constant over forecast period)
        minority_interest = self.minority_interest[0]
        self.minority_interest.append(minority_interest)
        
        # ===== TOTALS =====
        # Total L&E includes: Liabilities + Stockholders' Equity + Minority Interest
        total_liab_equity = total_liabilities + total_equity + minority_interest
        self.total_liabilities_equity.append(total_liab_equity)
        
        # Balance check - this shows the imbalance (should be 0 in a perfect model)
        check = total_assets - total_liab_equity
        self.balance_check.append(check)
    
    def get_summary(self) -> Dict[str, List[float]]:
        """Return balance sheet as a dictionary"""
        return {
            # Assets
            'Cash': self.cash,
            'Accounts Receivable': self.accounts_receivable,
            'Inventory': self.inventory,
            'ST Investment': self.st_investment,
            'Current Assets': self.current_assets,
            'Net PPE': self.net_ppe,
            'Goodwill': self.goodwill,
            'Total Assets': self.total_assets,
            # Liabilities
            'Accounts Payable': self.accounts_payable,
            'Short-term Debt': self.short_term_debt,
            'Current Liabilities': self.current_liabilities,
            'Long-term Debt': self.long_term_debt,
            'Total Liabilities': self.total_liabilities,
            # Equity
            'Retained Earnings': self.retained_earnings,
            'Other Equity': self.other_equity,
            'Total Equity': self.total_equity,
            'Minority Interest': self.minority_interest,
            # Check
            'Total Liabilities & Equity': self.total_liabilities_equity,
            'Balance Check (Assets - L&E)': self.balance_check,
        }

