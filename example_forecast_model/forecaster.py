"""
Main forecaster module.
Orchestrates the calculation of all forecast components.
"""

import pandas as pd
from .config import ForecastConfig
from .inputs import InputData
from .intermediate import IntermediateCalculations
from .cash_budget import CashBudget
from .debt_schedule import DebtSchedule
from .income_statement import IncomeStatement
from .balance_sheet import BalanceSheet


class Forecaster:
    """
    Main forecaster class that coordinates all calculations.
    
    Workflow:
    1. Calculate intermediate tables (sales, depreciation, inventory, etc.)
    2. For each year, iteratively calculate:
       - Cash budget (operating, investing, financing activities)
       - Debt schedules (ST and LT loans)
       - Income statement
       - Balance sheet
    """
    
    def __init__(self, input_file=None):
        """
        Initialize the forecaster
        
        Args:
            input_file: Path to input data file (optional)
        """
        self.config = ForecastConfig(n_years=4)
        self.inputs = InputData(input_file)
        
        self.intermediate = None
        self.cash_budget = None
        self.debt_schedule = None
        self.income_statement = None
        self.balance_sheet = None
    
    def run_forecast(self):
        """Execute the complete forecast"""
        print("=" * 80)
        print("FINANCIAL FORECASTING MODEL - MODULAR VERSION")
        print("=" * 80)
        
        # Step 1: Calculate intermediate tables
        print("\nStep 1: Calculating intermediate tables...")
        self.intermediate = IntermediateCalculations(self.inputs, self.config)
        self.intermediate.calculate_all()
        
        # Step 2: Initialize modules
        print("\nStep 2: Initializing forecast modules...")
        self.cash_budget = CashBudget(self.inputs, self.config, self.intermediate)
        self.debt_schedule = DebtSchedule(self.inputs, self.config)
        self.income_statement = IncomeStatement(self.inputs, self.config, self.intermediate)
        self.balance_sheet = BalanceSheet(self.inputs, self.config)
        
        # Calculate year 0 cash budget and initial financing
        print("\nCalculating Year 0 cash budget and initial financing...")
        st_loan_0, lt_loan_0, equity_0 = self.cash_budget.calculate_year_0(self.debt_schedule)
        print(f"  Year 0 ST Loan: ${st_loan_0:.2f}")
        print(f"  Year 0 LT Loan: ${lt_loan_0:.2f}")
        print(f"  Year 0 Equity Investment: ${equity_0:.2f}")
        
        # Initialize debt schedule with Year 0 loans
        self.debt_schedule.initialize_year_0_loans(st_loan_0, lt_loan_0)
        
        # Update balance sheet year 0 with calculated equity
        self.balance_sheet.equity_investment[0] = equity_0
        
        # Calculate year 0 balance sheet with debt schedule
        self.balance_sheet.calculate_year_0(self.intermediate, self.debt_schedule)
        
        # Calculate Year 0 income statement (for tax calculation in Year 1)
        # Year 0 has no revenue/sales, but may have expenses and interest
        # Since there's no sales in Year 0, we don't calculate full income statement
        # Tax for Year 0 will be 0 (no taxable income)
        year_0_tax = 0
        self.income_statement.income_taxes.append(year_0_tax)
        self.income_statement.ebt.append(0)
        self.income_statement.net_income.append(0)
        self.income_statement.interest_payments.append(0)  # No interest in Year 0
        
        # Step 3: Year-by-year iterative calculations
        print("\nStep 3: Year-by-year forecast calculations...")
        for year in range(1, self.config.n_years + 1):
            print(f"\n  Calculating Year {year}...")
            
            # Step 1: Calculate income statement (which calculates interest based on previous year's ending debt)
            self.income_statement.calculate_year(year, self.cash_budget, self.debt_schedule)
            
            # Step 2: Calculate cash budget (uses previous year's tax)
            self.cash_budget.calculate_year(year, self.debt_schedule, self.income_statement)
            
            # Step 3: Update debt schedules
            self.debt_schedule.update_st_debt(
                year, 
                self.cash_budget.st_loan[year],
                self.cash_budget.st_loan_principal_payment[year]
            )
            self.debt_schedule.update_lt_debt(
                year,
                self.cash_budget.lt_loan[year]
            )
            
            # Calculate balance sheet
            self.balance_sheet.calculate_year(
                year,
                self.intermediate,
                self.cash_budget,
                self.debt_schedule,
                self.income_statement
            )
        
        print("\n" + "=" * 80)
        print("FORECAST COMPLETE!")
        print("=" * 80)
    
    def print_summary(self):
        """Print a summary of forecast results"""
        print("\n" + "=" * 80)
        print("FORECAST SUMMARY")
        print("=" * 80)
        
        years_header = "Year" + "".join([f"{y:>15}" for y in self.config.years])
        
        # Income Statement
        print("\n--- INCOME STATEMENT ---")
        print(years_header)
        self._print_row("Sales Revenue", [0] + self.income_statement.sales_revenues)
        self._print_row("COGS", [0] + self.income_statement.cogs)
        self._print_row("Gross Income", [0] + self.income_statement.gross_income)
        self._print_row("EBIT", [0] + self.income_statement.ebit)
        self._print_row("Net Income", [0] + self.income_statement.net_income)
        
        # Balance Sheet
        print("\n--- BALANCE SHEET ---")
        print(years_header)
        print("ASSETS:")
        self._print_row("  Cash", self.balance_sheet.cash)
        self._print_row("  Total Assets", self.balance_sheet.total_assets)
        print("\nLIABILITIES & EQUITY:")
        self._print_row("  Total Liabilities", self.balance_sheet.total_liabilities)
        self._print_row("  Total Equity", self.balance_sheet.total_equity)
        self._print_row("  Check (should be 0)", self.balance_sheet.check_difference)
        
        # Cash Budget - Detailed
        print("\n--- CASH BUDGET SUMMARY ---")
        print(years_header)
        print("\nModule 1: Operating Activities")
        self._print_row("  Operating NCB", [0] + self.cash_budget.operating_ncb)
        
        print("\nModule 2: Investment Activities")
        self._print_row("  NCB of Investment in Assets", [0] + self.cash_budget.investment_ncb)
        
        print("\nModule 3: External Financing")
        self._print_row("  NCB of Financing Activities", [0] + self.cash_budget.financing_ncb)
        
        print("\nModule 4: Transactions with Owners")
        self._print_row("  NCB with Owners", [0] + self.cash_budget.ncb_with_owners)
        
        print("\nModule 5: Discretionary Transactions")
        self._print_row("  NCB of Discretionary Trans", [0] + self.cash_budget.discretionary_ncb)
        
        print("\nSummary:")
        self._print_row("  Year NCB", [0] + self.cash_budget.year_ncb)
        self._print_row("  Cumulated NCB", self.cash_budget.cumulated_ncb)
    
    def _print_row(self, label, values):
        """Helper to print a formatted row"""
        values_str = "".join([f"{v:>15.2f}" for v in values])
        print(f"{label:<30}{values_str}")
    
    def save_to_excel(self, filename="forecast_results.xlsx"):
        """
        Save forecast results to Excel file
        
        Args:
            filename: Output filename
        """
        print(f"\nSaving results to {filename}...")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Income Statement - Years as columns
            is_data = {
                'Sales Revenue': [0] + self.income_statement.sales_revenues,
                'COGS': [0] + self.income_statement.cogs,
                'Gross Income': [0] + self.income_statement.gross_income,
                'A&S Expenses': [0] + self.income_statement.as_expenses,
                'Depreciation': [0] + self.income_statement.depreciation,
                'EBIT': [0] + self.income_statement.ebit,
                'Interest Payments': [0] + self.income_statement.interest_payments,
                'ST Investment Return': [0] + self.income_statement.st_investment_return,
                'EBT': [0] + self.income_statement.ebt,
                'Income Taxes': [0] + self.income_statement.income_taxes,
                'Net Income': [0] + self.income_statement.net_income,
                'Next Year Dividends': [0] + self.income_statement.next_year_dividends,
                'Cumulated Retained Earnings': self.income_statement.cumulated_retained_earnings
            }
            df_is = pd.DataFrame(is_data, index=[f'Year {y}' for y in self.config.years]).T
            df_is.to_excel(writer, sheet_name='Income Statement')
            
            # Balance Sheet - Years as columns
            bs_data = {
                'Cash': self.balance_sheet.cash,
                'Accounts Receivable': self.balance_sheet.accounts_receivable,
                'Inventory': self.balance_sheet.inventory,
                'Advance Payments Paid': self.balance_sheet.advance_payments_paid,
                'ST Investment': self.balance_sheet.st_investment,
                'Current Assets': self.balance_sheet.current_assets,
                'Net Fixed Assets': self.balance_sheet.net_fixed_assets,
                'Total Assets': self.balance_sheet.total_assets,
                '': [''] * len(self.config.years),
                'Accounts Payable': self.balance_sheet.accounts_payable,
                'Advance Payments Received': self.balance_sheet.advance_payments_received,
                'Short-term Debt': self.balance_sheet.st_debt,
                'Current Liabilities': self.balance_sheet.current_liabilities,
                'Long-term Debt': self.balance_sheet.lt_debt,
                'Total Liabilities': self.balance_sheet.total_liabilities,
                ' ': [''] * len(self.config.years),
                'Equity Investment': self.balance_sheet.equity_investment,
                'Retained Earnings': self.balance_sheet.retained_earnings,
                'Current Year NI': self.balance_sheet.current_year_ni,
                'Total Equity': self.balance_sheet.total_equity,
                'Total Liab & Equity': self.balance_sheet.total_liab_equity,
                'Check Difference': self.balance_sheet.check_difference
            }
            df_bs = pd.DataFrame(bs_data, index=[f'Year {y}' for y in self.config.years]).T
            df_bs.to_excel(writer, sheet_name='Balance Sheet')
            
            # Cash Budget - Years as columns
            cb_data = {
                'Operating NCB': self.cash_budget.operating_ncb,
                'Investment NCB': self.cash_budget.investment_ncb,
                'ST Loan': self.cash_budget.st_loan,
                'LT Loan': self.cash_budget.lt_loan,
                'Total Loan Payment': self.cash_budget.total_loan_payment,
                'Financing NCB': self.cash_budget.financing_ncb,
                'Invested Equity': self.cash_budget.invested_equity,
                'Dividends Payment': self.cash_budget.dividends_payment,
                'NCB with Owners': self.cash_budget.ncb_with_owners,
                'ST Investment': self.cash_budget.st_investment,
                'Discretionary NCB': self.cash_budget.discretionary_ncb,
                'Year NCB': self.cash_budget.year_ncb,
                'Cumulated NCB': self.cash_budget.cumulated_ncb
            }
            df_cb = pd.DataFrame(cb_data, index=[f'Year {y}' for y in self.config.years]).T
            df_cb.to_excel(writer, sheet_name='Cash Budget')
        
        print(f"Results saved to {filename}")
