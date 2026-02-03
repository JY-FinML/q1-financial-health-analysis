"""
Main Forecaster module for company financial forecasting.
Orchestrates the calculation of all forecast components.

Uses the NO PLUG, NO CIRCULARITY approach:
1. Calculate Year 0 from historical data
2. Calculate intermediate values (revenue, costs, depreciation, etc.)
3. For each year:
   - Calculate income statement (interest based on beginning-of-year debt)
   - Calculate cash budget (determines financing needs)
   - Update debt schedule
   - Calculate balance sheet
"""

import pandas as pd
import os
from typing import Optional

from .config import ForecastConfig, ModelAssumptions
from .data_loader import DataLoader
from .input_calculator import InputCalculator
from .intermediate import IntermediateCalculations
from .income_statement import IncomeStatement
from .balance_sheet import BalanceSheet
from .cash_budget import CashBudget
from .debt_schedule import DebtSchedule


class CompanyForecaster:
    """
    Main forecaster class that coordinates all calculations.
    
    Workflow:
    1. Load historical data
    2. Calculate inputs from historical data
    3. Calculate intermediate values
    4. Year 0: Initialize from historical data
    5. Years 1-N: Iteratively calculate:
       - Income statement (with interest from beginning debt)
       - Cash budget (operating, investing, financing)
       - Debt schedule updates
       - Balance sheet
    """
    
    def __init__(self, company_folder: str, n_forecast_years: int = 4, 
                 n_input_years: int = 3, assumptions: ModelAssumptions = None,
                 base_year: str = None):
        """
        Initialize the forecaster
        
        Args:
            company_folder: Path to folder containing company CSV files
            n_forecast_years: Number of years to forecast (default 4)
            n_input_years: Number of historical years to use for calculating ratios (default 3)
            assumptions: ModelAssumptions (optional)
            base_year: Base year (Year 0) for forecasting. If None, uses latest available year.
        """
        self.company_folder = company_folder
        self.company_name = os.path.basename(company_folder)
        self.base_year_override = base_year  # Store the override
        
        # Configuration
        self.config = ForecastConfig(n_forecast_years=n_forecast_years, n_input_years=n_input_years)
        self.assumptions = assumptions or ModelAssumptions()
        
        # Components
        self.data_loader: Optional[DataLoader] = None
        self.input_calculator: Optional[InputCalculator] = None
        self.inputs: dict = {}
        
        self.intermediate: Optional[IntermediateCalculations] = None
        self.income_statement: Optional[IncomeStatement] = None
        self.balance_sheet: Optional[BalanceSheet] = None
        self.cash_budget: Optional[CashBudget] = None
        self.debt_schedule: Optional[DebtSchedule] = None
    
    def run_forecast(self):
        """Execute the complete forecast"""
        print("=" * 80)
        print(f"FINANCIAL FORECAST: {self.company_name}")
        print("No Plug, No Circularity Method")
        print("=" * 80)
        
        # Step 1: Load historical data
        print("\nStep 1: Loading historical data...")
        self.data_loader = DataLoader(self.company_folder)
        if not self.data_loader.load_all():
            raise ValueError(f"Failed to load data for {self.company_name}")
        
        # Set base year - use override if provided, otherwise latest year
        if self.base_year_override:
            self.data_loader.set_base_year(self.base_year_override)
            self.config.base_year = int(self.base_year_override)
        elif self.data_loader.latest_year:
            self.config.base_year = int(self.data_loader.latest_year)
        
        # Step 2: Calculate inputs from historical data
        print("\nStep 2: Calculating forecast inputs...")
        self.input_calculator = InputCalculator(
            self.data_loader, 
            self.config, 
            self.assumptions
        )
        self.inputs = self.input_calculator.calculate_all_inputs()
        print(self.input_calculator.get_summary())
        
        # Step 3: Calculate intermediate values
        print("\nStep 3: Calculating intermediate values...")
        self.intermediate = IntermediateCalculations(self.inputs, self.config)
        self.intermediate.calculate_all()
        
        # Step 4: Initialize modules
        print("\nStep 4: Initializing forecast modules...")
        self.debt_schedule = DebtSchedule(self.inputs, self.config)
        self.cash_budget = CashBudget(self.inputs, self.config, self.intermediate)
        self.income_statement = IncomeStatement(self.inputs, self.config, self.intermediate)
        self.balance_sheet = BalanceSheet(self.inputs, self.config)
        
        # Step 5: Calculate Year 0
        print("\nStep 5: Calculating Year 0...")
        st_debt_0, lt_debt_0, equity_0 = self.cash_budget.calculate_year_0(self.debt_schedule)
        self.debt_schedule.initialize_year_0(st_debt_0, lt_debt_0)
        
        print(f"  Year 0 ST Debt: ${st_debt_0:,.0f}")
        print(f"  Year 0 LT Debt: ${lt_debt_0:,.0f}")
        print(f"  Year 0 Cash: ${self.inputs['cash_year_0']:,.0f}")
        
        # Step 6: Year-by-year iterative calculations
        print("\nStep 6: Year-by-year forecast calculations...")
        for year in range(1, self.config.n_forecast_years + 1):
            print(f"\n  Calculating Year {year} ({self.config.base_year + year})...")
            
            # 1. Calculate income statement (interest based on beginning-of-year debt)
            self.income_statement.calculate_year(year, self.cash_budget, self.debt_schedule)
            
            # 2. Calculate cash budget
            self.cash_budget.calculate_year(year, self.debt_schedule, self.income_statement)
            
            # 3. Update debt schedules
            self.debt_schedule.update_st_debt(
                year,
                self.cash_budget.st_loan[year],
                self.cash_budget.st_principal_payment[year]
            )
            self.debt_schedule.update_lt_debt(
                year,
                self.cash_budget.lt_loan[year]
            )
            
            # 4. Calculate balance sheet
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
        
        years_header = "Year" + "".join([f"{y:>15}" for y in self.config.year_labels])
        
        # Income Statement
        print("\n--- INCOME STATEMENT ($ millions) ---")
        print(years_header)
        self._print_row("Revenue", self.income_statement.revenue)
        self._print_row("COGS", self.income_statement.cogs)
        self._print_row("Gross Profit", self.income_statement.gross_profit)
        self._print_row("SG&A", self.income_statement.sga_expenses)
        self._print_row("Depreciation", self.income_statement.depreciation)
        self._print_row("Operating Income", self.income_statement.operating_income)
        self._print_row("Interest Expense", self.income_statement.interest_expense)
        self._print_row("EBT", self.income_statement.ebt)
        self._print_row("Income Taxes", self.income_statement.income_taxes)
        self._print_row("Net Income", self.income_statement.net_income)
        
        # Balance Sheet
        print("\n--- BALANCE SHEET ($ millions) ---")
        print(years_header)
        print("ASSETS:")
        self._print_row("  Cash", self.balance_sheet.cash)
        self._print_row("  Accounts Receivable", self.balance_sheet.accounts_receivable)
        self._print_row("  Inventory", self.balance_sheet.inventory)
        self._print_row("  Current Assets", self.balance_sheet.current_assets)
        self._print_row("  Net PPE", self.balance_sheet.net_ppe)
        self._print_row("  Total Assets", self.balance_sheet.total_assets)
        print("\nLIABILITIES:")
        self._print_row("  Accounts Payable", self.balance_sheet.accounts_payable)
        self._print_row("  Short-term Debt", self.balance_sheet.short_term_debt)
        self._print_row("  Current Liabilities", self.balance_sheet.current_liabilities)
        self._print_row("  Long-term Debt", self.balance_sheet.long_term_debt)
        self._print_row("  Total Liabilities", self.balance_sheet.total_liabilities)
        print("\nEQUITY:")
        self._print_row("  Retained Earnings", self.balance_sheet.retained_earnings)
        self._print_row("  Total Equity", self.balance_sheet.total_equity)
        print("\nCHECK:")
        self._print_row("  Total L + E", self.balance_sheet.total_liabilities_equity)
        self._print_row("  Balance Check", self.balance_sheet.balance_check)
        
        # Cash Budget
        print("\n--- CASH BUDGET ($ millions) ---")
        print(years_header)
        self._print_row("Operating CF", self.cash_budget.operating_cash_flow)
        self._print_row("Investing CF", self.cash_budget.investing_cash_flow)
        self._print_row("Financing CF", self.cash_budget.financing_cash_flow)
        self._print_row("Year NCB", self.cash_budget.year_ncb)
        self._print_row("Ending Cash", self.cash_budget.cumulated_ncb)
    
    def _print_row(self, label: str, values: list):
        """Helper to print a formatted row"""
        values_str = "".join([f"{v:>15,.0f}" for v in values])
        print(f"{label:<25}{values_str}")
    
    def save_to_excel(self, filename: str = None):
        """
        Save forecast results to Excel file
        
        Args:
            filename: Output filename (default: {company_name}_forecast.xlsx)
        """
        if filename is None:
            filename = f"{self.company_name}_forecast.xlsx"
        
        print(f"\nSaving results to {filename}...")
        
        # Create year labels for columns
        year_labels = self.config.year_labels
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Income Statement
            is_data = self.income_statement.get_summary()
            is_df = pd.DataFrame(is_data, index=year_labels).T
            is_df.to_excel(writer, sheet_name='Income Statement')
            
            # Balance Sheet
            bs_data = self.balance_sheet.get_summary()
            bs_df = pd.DataFrame(bs_data, index=year_labels).T
            bs_df.to_excel(writer, sheet_name='Balance Sheet')
            
            # Cash Budget
            cb_data = self.cash_budget.get_summary()
            cb_df = pd.DataFrame(cb_data, index=year_labels).T
            cb_df.to_excel(writer, sheet_name='Cash Budget')
            
            # Debt Schedule
            ds_data = self.debt_schedule.get_summary()
            ds_df = pd.DataFrame(ds_data, index=year_labels).T
            ds_df.to_excel(writer, sheet_name='Debt Schedule')
            
            # Intermediate Calculations
            int_data = {
                'Revenue': self.intermediate.revenue,
                'COGS': self.intermediate.cogs,
                'Gross Profit': self.intermediate.gross_profit,
                'SG&A': self.intermediate.sga_expenses,
                'Depreciation': self.intermediate.depreciation,
                'CapEx': self.intermediate.capex,
                'Net PPE': self.intermediate.net_ppe,
                'Accounts Receivable': self.intermediate.accounts_receivable,
                'Inventory': self.intermediate.inventory,
                'Accounts Payable': self.intermediate.accounts_payable,
                'Min Cash Required': self.intermediate.min_cash_required,
            }
            int_df = pd.DataFrame(int_data, index=year_labels).T
            int_df.to_excel(writer, sheet_name='Intermediate')
            
            # Input Summary
            inputs_summary = {
                'Parameter': list(self.inputs.keys()),
                'Value': [str(v) for v in self.inputs.values()]
            }
            inputs_df = pd.DataFrame(inputs_summary)
            inputs_df.to_excel(writer, sheet_name='Inputs', index=False)
        
        print(f"✓ Results saved to {filename}")
        
        return filename
