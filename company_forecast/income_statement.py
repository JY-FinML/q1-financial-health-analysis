"""
Income Statement module for company forecasting.
Calculates revenues, expenses, interest, taxes, and net income.
"""

from typing import Dict, List
from .config import ForecastConfig


class IncomeStatement:
    """
    Handles income statement calculations including:
    - Revenue (from intermediate)
    - Cost of goods sold
    - Gross profit
    - Operating expenses (SG&A + Depreciation)
    - Operating income (EBIT)
    - Interest expense (based on debt schedule)
    - Interest income (from ST investments)
    - Pretax income (EBT)
    - Income taxes
    - Net income
    - Dividends
    """
    
    def __init__(self, inputs: Dict, config: ForecastConfig, intermediate):
        """
        Initialize income statement
        
        Args:
            inputs: Dictionary of calculated inputs
            config: ForecastConfig object
            intermediate: IntermediateCalculations object
        """
        self.inputs = inputs
        self.config = config
        self.intermediate = intermediate
        self.n_years = config.n_forecast_years
        
        # Income statement items (Year 0 values from historical data)
        self.revenue = [inputs['revenue_year_0']]
        self.cogs = [inputs['cogs_year_0']]
        self.gross_profit = [inputs['gross_profit_year_0']]
        self.sga_expenses = [inputs['sga_year_0']]
        self.depreciation = [inputs['depreciation_year_0']]
        self.operating_income = [inputs['operating_income_year_0']]
        
        self.interest_expense = [inputs['interest_expense_year_0']]
        self.interest_income = [0]  # ST investment return
        
        self.ebt = [inputs['pretax_income_year_0']]
        self.income_taxes = [inputs['tax_provision_year_0']]
        self.net_income = [inputs['net_income_year_0']]
        
        # Dividends (next year's dividends based on this year's NI)
        self.dividends = [inputs['dividends_paid_year_0']]
        
        # Retained earnings
        self.cumulated_retained_earnings = [inputs['retained_earnings_year_0']]
    
    def calculate_year(self, year: int, cash_budget, debt_schedule):
        """
        Calculate income statement for a specific year
        
        Uses the no-circularity approach:
        1. Interest is calculated on BEGINNING of year debt (= previous year end debt)
        2. Tax is calculated on current year's EBT
        
        Args:
            year: Year number (1-4)
            cash_budget: CashBudget object
            debt_schedule: DebtSchedule object with beginning balances
        """
        i = year - 1  # 0-based index for arrays
        
        # Revenue and COGS from intermediate calculations
        revenue = self.intermediate.revenue[year]
        cogs = self.intermediate.cogs[year]
        gross_profit = self.intermediate.gross_profit[year]
        
        self.revenue.append(revenue)
        self.cogs.append(cogs)
        self.gross_profit.append(gross_profit)
        
        # Operating expenses
        sga = self.intermediate.sga_expenses[year]
        depreciation = self.intermediate.depreciation[year]
        
        self.sga_expenses.append(sga)
        self.depreciation.append(depreciation)
        
        # Operating income (EBIT)
        operating_income = gross_profit - sga - depreciation
        self.operating_income.append(operating_income)
        
        # Interest expense: calculated on previous year's ENDING debt balance
        # This is the "no circularity" approach - we use beginning-of-year debt
        st_debt_begin = debt_schedule.st_ending_balance[year - 1]
        lt_debt_begin = debt_schedule.lt_ending_balance[year - 1]
        
        cost_of_debt = self.intermediate.cost_of_debt[i]
        
        st_interest = st_debt_begin * cost_of_debt if st_debt_begin > 0 else 0
        lt_interest = lt_debt_begin * cost_of_debt if lt_debt_begin > 0 else 0
        interest_expense = st_interest + lt_interest
        
        self.interest_expense.append(interest_expense)
        
        # Interest income: return on previous year's ST investments
        # Year 1: no prior investment
        # Year 2+: use previous year's investment
        interest_income = 0
        if year > 1 and len(cash_budget.st_investment) >= year:
            prev_investment = cash_budget.st_investment[year - 1]
            if prev_investment > 0:
                return_rate = self.intermediate.return_st_investment[i]
                interest_income = prev_investment * return_rate
        
        self.interest_income.append(interest_income)
        
        # Earnings before taxes (EBT)
        ebt = operating_income - interest_expense + interest_income
        self.ebt.append(ebt)
        
        # Income taxes (only if positive EBT)
        tax_rate = self.inputs['tax_rate']
        income_tax = max(0, ebt * tax_rate)
        self.income_taxes.append(income_tax)
        
        # Net income
        net_income = ebt - income_tax
        self.net_income.append(net_income)
        
        # Dividends (payout of current year's net income, paid next year)
        payout_ratio = self.inputs['payout_ratio']
        dividends = max(0, net_income * payout_ratio)
        self.dividends.append(dividends)
        
        # Cumulated retained earnings
        # = Previous cumulated RE + Previous year's Net Income - Previous year's Dividends
        prev_cum_re = self.cumulated_retained_earnings[year - 1]
        prev_ni = self.net_income[year - 1]
        prev_div = self.dividends[year - 1]
        
        cum_re = prev_cum_re + prev_ni - prev_div
        self.cumulated_retained_earnings.append(cum_re)
    
    def get_summary(self) -> Dict[str, List[float]]:
        """Return income statement as a dictionary"""
        return {
            'Revenue': self.revenue,
            'COGS': self.cogs,
            'Gross Profit': self.gross_profit,
            'SG&A': self.sga_expenses,
            'Depreciation': self.depreciation,
            'Operating Income': self.operating_income,
            'Interest Expense': self.interest_expense,
            'Interest Income': self.interest_income,
            'EBT': self.ebt,
            'Income Taxes': self.income_taxes,
            'Net Income': self.net_income,
            'Dividends': self.dividends,
        }
