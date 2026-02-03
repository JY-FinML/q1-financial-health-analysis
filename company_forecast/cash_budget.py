"""
Cash Budget module for company forecasting.
Calculates cash flows from operating, investing, financing, and discretionary activities.

Uses the NO PLUG, NO CIRCULARITY approach:
- Year 0: Calculate initial financing needs based on historical data
- Years 1-N: Calculate cash flows using beginning-of-year debt for interest
"""

from typing import Dict, List, Tuple
from .config import ForecastConfig


class CashBudget:
    """
    Handles cash budget calculations including:
    - Module 1: Operating activities (EBIT + Depreciation - Taxes - ΔWC)
    - Module 2: Investment activities (CapEx)
    - Module 3: External financing (ST and LT loans)
    - Module 4: Transactions with owners (Dividends, Equity)
    - Module 5: Discretionary transactions (ST investments)
    """
    
    def __init__(self, inputs: Dict, config: ForecastConfig, intermediate):
        """
        Initialize cash budget
        
        Args:
            inputs: Dictionary of calculated inputs
            config: ForecastConfig object
            intermediate: IntermediateCalculations object
        """
        self.inputs = inputs
        self.config = config
        self.intermediate = intermediate
        self.n_years = config.n_forecast_years
        
        # Module 1: Operating activities
        self.operating_cash_flow = []
        
        # Module 2: Investment activities
        self.investing_cash_flow = []
        
        # Module 3: External financing
        self.st_loan = []
        self.lt_loan = []
        self.st_principal_payment = []
        self.st_interest_payment = []
        self.lt_principal_payment = []
        self.lt_interest_payment = []
        self.financing_cash_flow = []
        
        # Module 4: Transactions with owners
        self.dividends_paid = []
        self.stock_repurchase = []
        self.equity_invested = []
        self.owner_cash_flow = []
        
        # Module 5: Discretionary
        self.st_investment = []
        self.st_investment_redemption = []
        self.st_investment_return = []
        self.discretionary_cash_flow = []
        
        # Summary
        self.year_ncb = []  # Net cash balance for the year
        self.cumulated_ncb = []  # Cumulative cash balance (ending cash)
        
        self.year_0_calculated = False
    
    def calculate_year_0(self, debt_schedule) -> Tuple[float, float, float]:
        """
        Calculate Year 0 initial state from historical data.
        
        For Year 0, we use historical ending balances:
        - Cash = Historical cash balance
        - ST Debt = Historical short-term debt
        - LT Debt = Historical long-term debt
        - Equity = Historical equity
        
        Returns:
            Tuple of (st_loan_0, lt_loan_0, equity_invested_0)
        """
        # Year 0 values come from historical data - no new financing needed
        st_debt_0 = self.inputs['short_term_debt_year_0']
        lt_debt_0 = self.inputs['long_term_debt_year_0']
        cash_0 = self.inputs['cash_year_0']
        
        # Initialize Year 0 arrays with zeros (no cash flow in Year 0, just balances)
        self.operating_cash_flow.insert(0, self.inputs['operating_cash_flow_year_0'])
        self.investing_cash_flow.insert(0, -self.inputs['capex_year_0'])
        
        # No new loans in Year 0 - we're just capturing the starting position
        self.st_loan.insert(0, 0)
        self.lt_loan.insert(0, 0)
        self.st_principal_payment.insert(0, 0)
        self.st_interest_payment.insert(0, 0)
        self.lt_principal_payment.insert(0, 0)
        self.lt_interest_payment.insert(0, 0)
        self.financing_cash_flow.insert(0, 0)
        
        self.dividends_paid.insert(0, self.inputs['dividends_paid_year_0'])
        self.stock_repurchase.insert(0, self.inputs['stock_repurchase_year_0'])
        self.equity_invested.insert(0, 0)
        self.owner_cash_flow.insert(0, -self.inputs['dividends_paid_year_0'] - self.inputs['stock_repurchase_year_0'])
        
        self.st_investment.insert(0, 0)
        self.st_investment_redemption.insert(0, 0)
        self.st_investment_return.insert(0, 0)
        self.discretionary_cash_flow.insert(0, 0)
        
        self.year_ncb.insert(0, 0)
        self.cumulated_ncb.insert(0, cash_0)  # Starting cash position
        
        self.year_0_calculated = True
        
        # Return the existing debt levels (not new loans)
        return st_debt_0, lt_debt_0, 0
    
    def calculate_year(self, year: int, debt_schedule, income_statement):
        """
        Calculate cash budget for a specific year.
        
        Uses the no-circularity approach:
        1. Operating CF = Net Income + Depreciation - Change in Working Capital
           (Interest is already deducted from Net Income, so no need to pay it separately)
        2. Investing CF = -CapEx
        3. Financing CF = New borrowing - Principal repayments
        4. Owner CF = New equity - Dividends - Repurchases
        
        Key insight: Interest payments are ALREADY reflected in Net Income reduction,
        so we only track PRINCIPAL payments in financing activities.
        
        Args:
            year: Year number (1-4)
            debt_schedule: DebtSchedule object
            income_statement: IncomeStatement object
        """
        i = year - 1  # 0-based index
        
        # ===== MODULE 1: OPERATING ACTIVITIES =====
        # Operating Cash Flow = Net Income + Depreciation - Change in Working Capital
        # Note: Interest expense is already included (reduces Net Income)
        
        net_income = income_statement.net_income[year]
        depreciation = self.intermediate.depreciation[year]
        change_wc = self.intermediate.change_in_working_capital[i]
        
        # Operating Cash Flow (interest is already in NI, don't double count)
        operating_cf = net_income + depreciation - change_wc
        self.operating_cash_flow.append(operating_cf)
        
        # ===== MODULE 2: INVESTING ACTIVITIES =====
        capex = self.intermediate.capex[year]
        investing_cf = -capex
        self.investing_cash_flow.append(investing_cf)
        
        # ===== DIVIDENDS AND REPURCHASES =====
        # Dividends from previous year's declaration
        if year > 1:
            dividends = income_statement.dividends[year - 1]
        else:
            dividends = self.inputs['dividends_paid_year_0']
        
        # Stock repurchase (simplified)
        stock_repurchase = self.inputs['stock_repurchase_year_0'] * 0.3
        
        self.dividends_paid.append(dividends)
        self.stock_repurchase.append(stock_repurchase)
        
        # ===== MODULE 5: DISCRETIONARY (ST Investment) =====
        # Redeem previous year's ST investment
        st_inv_redemption = self.st_investment[year - 1] if year > 0 else 0
        return_rate = self.intermediate.return_st_investment[i]
        st_inv_return = st_inv_redemption * return_rate if st_inv_redemption > 0 else 0
        
        self.st_investment_redemption.append(st_inv_redemption)
        self.st_investment_return.append(st_inv_return)
        
        # ===== MODULE 3: CALCULATE FINANCING NEEDS =====
        prev_cash = self.cumulated_ncb[year - 1]
        min_cash = self.intermediate.min_cash_required[year]
        
        # Debt service - ONLY PRINCIPAL (interest is already in Operating CF via Net Income)
        st_beginning = debt_schedule.st_ending_balance[year - 1]
        lt_beginning = debt_schedule.lt_ending_balance[year - 1]
        cost_of_debt = self.intermediate.cost_of_debt[i]
        
        # ST loan: repay full beginning balance (principal only)
        st_principal = st_beginning  # Full repayment for 1-year loan
        st_interest = st_beginning * cost_of_debt if st_beginning > 0 else 0  # For tracking only
        
        # LT loan: principal payment based on amortization
        lt_principal = debt_schedule.get_total_lt_principal_payment(year)
        lt_interest = lt_beginning * cost_of_debt if lt_beginning > 0 else 0  # For tracking only
        
        # Only principal affects cash in financing activities (interest is in operating via NI)
        total_principal_payment = st_principal + lt_principal
        
        self.st_principal_payment.append(st_principal)
        self.st_interest_payment.append(st_interest)  # For reference only
        self.lt_principal_payment.append(lt_principal)
        self.lt_interest_payment.append(lt_interest)  # For reference only
        
        # Cash before new financing (only principal payments affect cash here)
        cash_before_financing = (prev_cash 
                                + operating_cf 
                                + investing_cf 
                                - total_principal_payment  # Only principal, not interest
                                - dividends 
                                - stock_repurchase
                                + st_inv_redemption 
                                + st_inv_return)
        
        # Financing need = min_cash - cash_before_financing
        financing_need = max(0, min_cash - cash_before_financing)
        
        if financing_need > 0:
            debt_pct = self.inputs['pct_financing_with_debt']
            st_loan = financing_need * 0.3
            remaining_need = financing_need - st_loan
            lt_loan = remaining_need * debt_pct
            equity_invested = remaining_need * (1 - debt_pct)
        else:
            st_loan = 0
            lt_loan = 0
            equity_invested = 0
        
        self.st_loan.append(st_loan)
        self.lt_loan.append(lt_loan)
        self.equity_invested.append(equity_invested)
        
        # Financing cash flow = new loans - principal payments only
        financing_cf = st_loan + lt_loan - total_principal_payment
        self.financing_cash_flow.append(financing_cf)
        
        # Owner cash flow = equity invested - dividends - repurchases
        owner_cf = equity_invested - dividends - stock_repurchase
        self.owner_cash_flow.append(owner_cf)
        
        # ===== ST INVESTMENT =====
        cash_after_all = (prev_cash 
                         + operating_cf 
                         + investing_cf 
                         + financing_cf 
                         + owner_cf
                         + st_inv_redemption 
                         + st_inv_return)
        
        excess_cash = max(0, cash_after_all - min_cash)
        
        if financing_need == 0 and excess_cash > 0:
            st_investment = excess_cash * 0.5
        else:
            st_investment = 0
        
        self.st_investment.append(st_investment)
        
        discretionary_cf = st_inv_redemption + st_inv_return - st_investment
        self.discretionary_cash_flow.append(discretionary_cf)
        
        # ===== YEAR SUMMARY =====
        year_ncb = operating_cf + investing_cf + financing_cf + owner_cf + discretionary_cf
        cumulated_ncb = prev_cash + year_ncb
        
        self.year_ncb.append(year_ncb)
        self.cumulated_ncb.append(cumulated_ncb)
    
    def get_summary(self) -> Dict[str, List[float]]:
        """Return cash budget as a dictionary"""
        return {
            'Operating Cash Flow': self.operating_cash_flow,
            'Investing Cash Flow': self.investing_cash_flow,
            'ST Loan': self.st_loan,
            'LT Loan': self.lt_loan,
            'ST Principal Payment': self.st_principal_payment,
            'LT Principal Payment': self.lt_principal_payment,
            'Financing Cash Flow': self.financing_cash_flow,
            'Dividends Paid': self.dividends_paid,
            'Equity Invested': self.equity_invested,
            'Owner Cash Flow': self.owner_cash_flow,
            'ST Investment': self.st_investment,
            'Discretionary Cash Flow': self.discretionary_cash_flow,
            'Year NCB': self.year_ncb,
            'Ending Cash': self.cumulated_ncb,
        }
