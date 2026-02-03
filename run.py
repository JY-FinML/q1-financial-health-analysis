#!/usr/bin/env python3
"""
Main Entry Point for Financial Forecasting

Unified command-line interface for all forecast operations.

Usage:
    python run.py forecast ProcterGamble           # Standard forecast (latest year as base)
    python run.py forecast ProcterGamble --full    # Full detailed output
    python run.py forecast ProcterGamble --base-year 2023  # Backtest mode (auto-detected)
    python run.py config                           # View all company configs
    python run.py config ProcterGamble             # View specific company config
    python run.py list                             # List available companies
    
Options:
    --base-year YEAR    Override base year (default: from config or latest)
    --years N           Number of years to forecast (default: from config or 2)
    --full              Show full hierarchical output
    --no-save           Don't save report to file
    
Note: Backtest mode is AUTO-DETECTED when forecast years have actual data available.
"""

import os
import sys
import argparse
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from company_forecast.forecaster import CompanyForecaster
from company_forecast.data_loader import DataLoader
from configs.base_config import load_company_config, list_available_companies


def run_forecast(company_name: str, base_year: str = None, n_forecast_years: int = None, 
                 full_output: bool = False, save_report: bool = True) -> str:
    """
    Run forecast for a company.
    
    Args:
        company_name: Name of company folder
        base_year: Override base year (None = use config or latest)
        n_forecast_years: Override forecast years (None = use config or 2)
        full_output: Whether to show full hierarchical output
        save_report: Whether to save report to file
    """
    # Load config
    try:
        config = load_company_config(company_name)
    except Exception as e:
        print(f"Warning: Could not load config for {company_name}: {e}")
        config = None
    
    # Determine settings (CLI overrides > config > defaults)
    if base_year is None:
        base_year = str(config.base_year) if config and config.base_year else None
    else:
        base_year = str(base_year)
        
    if n_forecast_years is None:
        n_forecast_years = config.n_forecast_years if config else 2
    
    n_input_years = config.n_input_years if config else 3
    
    company_folder = os.path.join(project_root, "data", company_name)
    
    # Load data to check available years
    loader = DataLoader(company_folder)
    loader.load_all()
    available_years = loader.years
    
    # Auto-adjust n_input_years based on base_year
    if base_year and base_year in available_years:
        base_idx = available_years.index(base_year)
        available_input_years = len(available_years) - base_idx
        n_input_years = min(n_input_years, available_input_years)
        input_years_used = available_years[base_idx:base_idx + n_input_years]
    else:
        input_years_used = available_years[:n_input_years]
    
    # Determine actual base year
    actual_base_year = base_year if base_year else available_years[0]
    forecast_years = [str(int(actual_base_year) + i) for i in range(1, n_forecast_years + 1)]
    
    # Check if this is effectively a backtest
    is_backtest = any(y in available_years for y in forecast_years)
    
    # Run forecast
    print(f"\n{'='*80}")
    print(f"FORECAST: {company_name}")
    print(f"{'='*80}")
    print(f"Base Year:        {actual_base_year}")
    print(f"Input Years:      {input_years_used}")
    print(f"Forecast Years:   {forecast_years}")
    if is_backtest:
        print(f"Mode:             BACKTEST (actual data available for comparison)")
    print(f"{'='*80}\n")
    
    forecaster = CompanyForecaster(
        company_folder,
        n_forecast_years=n_forecast_years,
        n_input_years=n_input_years,
        base_year=base_year
    )
    forecaster.run_forecast()
    
    # Build display years (always show 4 years: mix of actual + estimated)
    min_display_years = 4
    total_model_years = n_forecast_years + 1  # base year + forecast years
    
    display_years = []  # List of (year_str, is_estimated, data_index_or_none)
    
    # First, add historical years before base year (if needed to reach 4 years)
    base_year_int = int(actual_base_year)
    if total_model_years < min_display_years:
        years_needed = min_display_years - total_model_years
        for i in range(years_needed, 0, -1):
            hist_year = str(base_year_int - i)
            if hist_year in available_years:
                display_years.append((hist_year, False, None))  # Actual, load from CSV
    
    # Add base year (actual data, index 0 in model)
    display_years.append((actual_base_year, False, 0))
    
    # Add forecast years - these are ALWAYS "E" (Estimated) because they come from model
    for i, fy in enumerate(forecast_years, 1):
        # Forecast years are always marked as Estimated (E) - they are model predictions
        display_years.append((fy, True, i))  # True = Estimated
    
    # If still less than 4 years, extend forecast years
    while len(display_years) < min_display_years:
        next_year = str(int(display_years[-1][0]) + 1)
        display_years.append((next_year, True, None))  # Estimated but no model data
    
    # Generate output
    lines = []
    lines.append("=" * 100)
    lines.append(f"FORECAST REPORT: {company_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")
    lines.append("SETTINGS:")
    lines.append(f"  Base Year (Y0):     {actual_base_year}")
    lines.append(f"  Input Years Used:   {input_years_used}")
    lines.append(f"  Forecast Years:     {forecast_years}")
    lines.append(f"  Mode:               {'Backtest' if is_backtest else 'Forecast'}")
    lines.append(f"  Display:            {[y[0] + ('E' if y[1] else 'A') for y in display_years]}")
    lines.append("")
    
    if full_output:
        # Full hierarchical output
        lines.extend(_generate_full_output(forecaster, loader, display_years))
    else:
        # Compact output
        lines.extend(_generate_compact_output(forecaster, loader, display_years))
    
    # Add backtest comparison if applicable
    if is_backtest:
        lines.append("")
        lines.extend(_generate_backtest_comparison(forecaster, company_folder, actual_base_year, forecast_years, n_forecast_years))
    
    report = "\n".join(lines)
    print(report)
    
    # Save report
    if save_report:
        mode_str = "backtest" if is_backtest else "forecast"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"results/{mode_str}_{company_name}_{timestamp}.txt"
        with open(os.path.join(project_root, filename), 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {filename}")
    
    return report


def _generate_compact_output(forecaster, loader, display_years):
    """Generate compact forecast output with A/E labels
    
    Args:
        forecaster: CompanyForecaster with model data
        loader: DataLoader with actual CSV data
        display_years: List of (year_str, is_estimated, model_index) tuples
    """
    lines = []
    
    # CSV field mappings for loading actual data
    is_csv_fields = {
        'revenue': 'Total Revenue',
        'cogs': 'Cost Of Revenue',
        'gross_profit': 'Gross Profit',
        'sga_expenses': 'Selling General And Administration',
        'depreciation': 'Reconciled Depreciation',
        'operating_income': 'Operating Income',
        'interest_expense': 'Interest Expense',
        'ebt': 'Pretax Income',
        'income_taxes': 'Tax Provision',
        'net_income': 'Net Income',
        'dividends': 'Cash Dividends Paid',
    }
    
    bs_csv_fields = {
        'cash': 'Cash Cash Equivalents And Short Term Investments',
        'accounts_receivable': 'Receivables',
        'inventory': 'Inventory',
        'current_assets': 'Current Assets',
        'net_ppe': 'Net PPE',
        'total_assets': 'Total Assets',
        'accounts_payable': 'Payables And Accrued Expenses',
        'short_term_debt': 'Current Debt And Capital Lease Obligation',
        'long_term_debt': 'Long Term Debt And Capital Lease Obligation',
        'total_liabilities': 'Total Liabilities Net Minority Interest',
        'retained_earnings': 'Retained Earnings',
        'total_equity': 'Stockholders Equity',
        'total_liabilities_equity': 'Total Liabilities Net Minority Interest',  # Will calculate
    }
    
    # Header with A/E labels
    header = f"{'Item':<30}"
    for year, is_est, _ in display_years:
        label = f"{year}{'E' if is_est else 'A'}"
        header += f"{label:>15}"
    
    # Income Statement
    lines.append("=" * 100)
    lines.append("INCOME STATEMENT")
    lines.append("=" * 100)
    lines.append(header)
    lines.append("-" * 100)
    
    is_items = [
        ('Revenue', 'revenue'),
        ('COGS', 'cogs'),
        ('Gross Profit', 'gross_profit'),
        ('SG&A Expense', 'sga_expenses'),
        ('Depreciation', 'depreciation'),
        ('Operating Income', 'operating_income'),
        ('Interest Expense', 'interest_expense'),
        ('EBT', 'ebt'),
        ('Tax Expense', 'income_taxes'),
        ('Net Income', 'net_income'),
        ('Dividends', 'dividends'),
    ]
    
    for label, attr in is_items:
        model_data = getattr(forecaster.income_statement, attr, [])
        row = f"{label:<30}"
        for year, is_est, model_idx in display_years:
            if model_idx is not None and model_idx < len(model_data):
                val = model_data[model_idx]
            else:
                # Load from CSV for historical data
                csv_field = is_csv_fields.get(attr)
                if csv_field:
                    val = loader.get_value('income', csv_field, year)
                    if attr == 'dividends':
                        val = loader.get_value('cash', csv_field, year)
                    val = abs(val) if val else 0
                else:
                    val = 0
            row += f"{val:>15,.0f}"
        lines.append(row)
    
    # Balance Sheet
    lines.append("")
    lines.append("=" * 100)
    lines.append("BALANCE SHEET")
    lines.append("=" * 100)
    lines.append(header)
    lines.append("-" * 100)
    
    bs_items = [
        ('Cash', 'cash'),
        ('Accounts Receivable', 'accounts_receivable'),
        ('Inventory', 'inventory'),
        ('Current Assets', 'current_assets'),
        ('Net PPE', 'net_ppe'),
        ('Total Assets', 'total_assets'),
        ('Accounts Payable', 'accounts_payable'),
        ('Short-term Debt', 'short_term_debt'),
        ('Long-term Debt', 'long_term_debt'),
        ('Total Liabilities', 'total_liabilities'),
        ('Retained Earnings', 'retained_earnings'),
        ('Total Equity', 'total_equity'),
        ('Minority Interest', 'minority_interest'),
        ('Total Liab & Equity', 'total_liabilities_equity'),
        ('Balance Check', 'balance_check'),
    ]
    
    for label, attr in bs_items:
        model_data = getattr(forecaster.balance_sheet, attr, [])
        row = f"{label:<30}"
        for year, is_est, model_idx in display_years:
            if model_idx is not None and model_idx < len(model_data):
                val = model_data[model_idx]
            else:
                # Load from CSV for historical data
                csv_field = bs_csv_fields.get(attr)
                if csv_field and attr != 'balance_check':
                    val = loader.get_value('balance', csv_field, year)
                    val = val if val else 0
                    # Calculate total_liabilities_equity
                    if attr == 'total_liabilities_equity':
                        liab = loader.get_value('balance', 'Total Liabilities Net Minority Interest', year) or 0
                        eq = loader.get_value('balance', 'Stockholders Equity', year) or 0
                        mi = loader.get_value('balance', 'Minority Interest', year) or 0
                        val = liab + eq + mi
                elif attr == 'balance_check':
                    assets = loader.get_value('balance', 'Total Assets', year) or 0
                    liab = loader.get_value('balance', 'Total Liabilities Net Minority Interest', year) or 0
                    eq = loader.get_value('balance', 'Stockholders Equity', year) or 0
                    mi = loader.get_value('balance', 'Minority Interest', year) or 0
                    val = assets - liab - eq - mi
                elif attr == 'minority_interest':
                    val = loader.get_value('balance', 'Minority Interest', year) or 0
                else:
                    val = 0
            row += f"{val:>15,.0f}"
        lines.append(row)
    
    return lines


def _generate_full_output(forecaster, loader, display_years):
    """Generate full hierarchical forecast output with A/E labels
    
    Args:
        forecaster: CompanyForecaster with model data
        loader: DataLoader with actual CSV data
        display_years: List of (year_str, is_estimated, model_index) tuples
    """
    lines = []
    
    # CSV field mappings
    is_csv_fields = {
        'revenue': ('income', 'Total Revenue'),
        'cogs': ('income', 'Cost Of Revenue'),
        'gross_profit': ('income', 'Gross Profit'),
        'sga_expenses': ('income', 'Selling General And Administration'),
        'depreciation': ('income', 'Reconciled Depreciation'),
        'operating_income': ('income', 'Operating Income'),
        'interest_expense': ('income', 'Interest Expense'),
        'interest_income': ('income', 'Interest Income'),
        'ebt': ('income', 'Pretax Income'),
        'income_taxes': ('income', 'Tax Provision'),
        'net_income': ('income', 'Net Income'),
        'dividends': ('cash', 'Cash Dividends Paid'),
    }
    
    bs_csv_fields = {
        'cash': 'Cash Cash Equivalents And Short Term Investments',
        'accounts_receivable': 'Receivables',
        'inventory': 'Inventory',
        'other_current_assets': 'Other Current Assets',
        'current_assets': 'Current Assets',
        'net_ppe': 'Net PPE',
        'goodwill': 'Goodwill',
        'intangible_assets': 'Other Intangible Assets',
        'other_non_current_assets': 'Other Non Current Assets',
        'total_non_current_assets': 'Total Non Current Assets',
        'total_assets': 'Total Assets',
        'accounts_payable': 'Payables And Accrued Expenses',
        'short_term_debt': 'Current Debt And Capital Lease Obligation',
        'other_current_liabilities': 'Other Current Liabilities',
        'current_liabilities': 'Current Liabilities',
        'long_term_debt': 'Long Term Debt And Capital Lease Obligation',
        'other_non_current_liabilities': 'Other Non Current Liabilities',
        'total_non_current_liabilities': 'Total Non Current Liabilities Net Minority Interest',
        'total_liabilities': 'Total Liabilities Net Minority Interest',
        'retained_earnings': 'Retained Earnings',
        'other_equity': 'Capital Stock',
        'total_equity': 'Stockholders Equity',
    }
    
    # Header with A/E labels
    header = f"{'Item':<45}"
    for year, is_est, _ in display_years:
        label = f"{year}{'E' if is_est else 'A'}"
        header += f"{label:>15}"
    
    # Income Statement
    lines.append("=" * 120)
    lines.append("INCOME STATEMENT (Full Detail)")
    lines.append("=" * 120)
    lines.append(header)
    lines.append("-" * 120)
    
    is_items = [
        ("Revenue", 'revenue'),
        ("  Cost of Revenue", 'cogs'),
        ("Gross Profit", 'gross_profit'),
        ("  SG&A Expense", 'sga_expenses'),
        ("  Depreciation", 'depreciation'),
        ("Operating Income", 'operating_income'),
        ("  Interest Expense", 'interest_expense'),
        ("  Interest Income (ST Inv)", 'interest_income'),
        ("Pretax Income (EBT)", 'ebt'),
        ("  Tax Expense", 'income_taxes'),
        ("Net Income", 'net_income'),
        ("  Dividends", 'dividends'),
    ]
    
    for label, attr in is_items:
        model_data = getattr(forecaster.income_statement, attr, [])
        row = f"{label:<45}"
        for year, is_est, model_idx in display_years:
            if model_idx is not None and model_idx < len(model_data):
                val = model_data[model_idx]
            else:
                # Load from CSV
                csv_info = is_csv_fields.get(attr)
                if csv_info:
                    stmt, field = csv_info
                    val = loader.get_value(stmt, field, year)
                    val = abs(val) if val else 0
                else:
                    val = 0
            row += f"{val:>15,.0f}"
        lines.append(row)
    
    # Balance Sheet
    lines.append("")
    lines.append("=" * 120)
    lines.append("BALANCE SHEET (Full Detail)")
    lines.append("=" * 120)
    lines.append(header)
    lines.append("-" * 120)
    
    bs_items = [
        ("ASSETS", None, None),
        ("  Cash & ST Investments", 'cash', forecaster.balance_sheet.cash),
        ("  Accounts Receivable", 'accounts_receivable', forecaster.balance_sheet.accounts_receivable),
        ("  Inventory", 'inventory', forecaster.balance_sheet.inventory),
        ("  Other Current Assets", 'other_current_assets', forecaster.balance_sheet.other_current_assets),
        ("Current Assets", 'current_assets', forecaster.balance_sheet.current_assets),
        ("  Net PP&E", 'net_ppe', forecaster.balance_sheet.net_ppe),
        ("  Goodwill", 'goodwill', forecaster.balance_sheet.goodwill),
        ("  Intangible Assets", 'intangible_assets', forecaster.balance_sheet.intangible_assets),
        ("  Other Non-Current Assets", 'other_non_current_assets', forecaster.balance_sheet.other_non_current_assets),
        ("Total Non-Current Assets", 'total_non_current_assets', forecaster.balance_sheet.total_non_current_assets),
        ("Total Assets", 'total_assets', forecaster.balance_sheet.total_assets),
        ("", None, None),
        ("LIABILITIES", None, None),
        ("  Accounts Payable", 'accounts_payable', forecaster.balance_sheet.accounts_payable),
        ("  Short-term Debt", 'short_term_debt', forecaster.balance_sheet.short_term_debt),
        ("  Other Current Liabilities", 'other_current_liabilities', forecaster.balance_sheet.other_current_liabilities),
        ("Current Liabilities", 'current_liabilities', forecaster.balance_sheet.current_liabilities),
        ("  Long-term Debt", 'long_term_debt', forecaster.balance_sheet.long_term_debt),
        ("  Other Non-Current Liabilities", 'other_non_current_liabilities', forecaster.balance_sheet.other_non_current_liabilities),
        ("Total Non-Current Liabilities", 'total_non_current_liabilities', forecaster.balance_sheet.total_non_current_liabilities),
        ("Total Liabilities", 'total_liabilities', forecaster.balance_sheet.total_liabilities),
        ("", None, None),
        ("EQUITY", None, None),
        ("  Retained Earnings", 'retained_earnings', forecaster.balance_sheet.retained_earnings),
        ("  Other Equity", 'other_equity', forecaster.balance_sheet.other_equity),
        ("Total Equity", 'total_equity', forecaster.balance_sheet.total_equity),
        ("Minority Interest", 'minority_interest', forecaster.balance_sheet.minority_interest),
        ("", None, None),
        ("Total Liab & Equity", 'total_liabilities_equity', forecaster.balance_sheet.total_liabilities_equity),
        ("Balance Check (A - L - E - MI)", 'balance_check', forecaster.balance_sheet.balance_check),
    ]
    
    for label, attr, model_data in bs_items:
        if attr is None:
            # Section header or blank line
            if label:
                lines.append(f"{label}")
            else:
                lines.append("")
        else:
            row = f"{label:<45}"
            for year, is_est, model_idx in display_years:
                if model_data is not None and model_idx is not None and model_idx < len(model_data):
                    val = model_data[model_idx]
                else:
                    # Load from CSV
                    csv_field = bs_csv_fields.get(attr)
                    if csv_field and attr not in ['balance_check', 'total_liabilities_equity']:
                        val = loader.get_value('balance', csv_field, year)
                        val = val if val else 0
                    elif attr == 'total_liabilities_equity':
                        liab = loader.get_value('balance', 'Total Liabilities Net Minority Interest', year) or 0
                        eq = loader.get_value('balance', 'Stockholders Equity', year) or 0
                        mi = loader.get_value('balance', 'Minority Interest', year) or 0
                        val = liab + eq + mi
                    elif attr == 'balance_check':
                        assets = loader.get_value('balance', 'Total Assets', year) or 0
                        liab = loader.get_value('balance', 'Total Liabilities Net Minority Interest', year) or 0
                        eq = loader.get_value('balance', 'Stockholders Equity', year) or 0
                        mi = loader.get_value('balance', 'Minority Interest', year) or 0
                        val = assets - liab - eq - mi
                    elif attr == 'minority_interest':
                        val = loader.get_value('balance', 'Minority Interest', year) or 0
                    else:
                        val = 0
                row += f"{val:>15,.0f}"
            lines.append(row)
    
    return lines


def _generate_backtest_comparison(forecaster, company_folder, base_year, forecast_years, n_forecast_years):
    """Generate backtest comparison with actual data, organized by year with full detail"""
    lines = []
    
    # Load full data
    full_loader = DataLoader(company_folder)
    full_loader.load_all()
    
    lines.append("=" * 120)
    lines.append("BACKTEST COMPARISON (Forecast vs Actual)")
    lines.append("=" * 120)
    
    # Income Statement items (matching full detail output)
    is_compare_items = [
        ('Revenue', 'revenue', 'Total Revenue'),
        ('  Cost of Revenue', 'cogs', 'Cost Of Revenue'),
        ('Gross Profit', 'gross_profit', 'Gross Profit'),
        ('  SG&A Expense', 'sga_expenses', 'Selling General And Administration'),
        ('  Depreciation', 'depreciation', 'Reconciled Depreciation'),
        ('Operating Income', 'operating_income', 'Operating Income'),
        ('  Interest Expense', 'interest_expense', 'Interest Expense'),
        ('Pretax Income (EBT)', 'ebt', 'Pretax Income'),
        ('  Tax Expense', 'income_taxes', 'Tax Provision'),
        ('Net Income', 'net_income', 'Net Income'),
    ]
    
    # Balance Sheet items (matching full detail output)
    bs_compare_items = [
        ('Cash & ST Investments', 'cash', 'Cash Cash Equivalents And Short Term Investments'),
        ('Accounts Receivable', 'accounts_receivable', 'Receivables'),
        ('Inventory', 'inventory', 'Inventory'),
        ('Current Assets', 'current_assets', 'Current Assets'),
        ('Net PP&E', 'net_ppe', 'Net PPE'),
        ('Total Assets', 'total_assets', 'Total Assets'),
        ('Accounts Payable', 'accounts_payable', 'Payables And Accrued Expenses'),
        ('Short-term Debt', 'short_term_debt', 'Current Debt And Capital Lease Obligation'),
        ('Current Liabilities', 'current_liabilities', 'Current Liabilities'),
        ('Long-term Debt', 'long_term_debt', 'Long Term Debt And Capital Lease Obligation'),
        ('Total Liabilities', 'total_liabilities', 'Total Liabilities Net Minority Interest'),
        ('Retained Earnings', 'retained_earnings', 'Retained Earnings'),
        ('Total Equity', 'total_equity', 'Stockholders Equity'),
    ]
    
    all_year_errors = {}  # {year: {'is': [], 'bs': []}}
    
    # Display by year
    for i, year in enumerate(forecast_years, 1):
        lines.append("")
        lines.append(f"{'='*120}")
        lines.append(f"YEAR {i} ({year})")
        lines.append(f"{'='*120}")
        
        year_is_errors = []
        year_bs_errors = []
        
        # Income Statement comparison
        lines.append("")
        lines.append("INCOME STATEMENT")
        lines.append(f"{'Item':<35} {'Forecast':>15} {'Actual':>15} {'Diff':>12} {'Error%':>10}")
        lines.append("-" * 90)
        
        for label, attr, csv_field in is_compare_items:
            forecast_data = getattr(forecaster.income_statement, attr, [])
            forecast_val = forecast_data[i] if i < len(forecast_data) else 0
            actual_val = full_loader.get_value('income', csv_field, year)
            
            if actual_val is not None and actual_val != 0:
                diff = forecast_val - actual_val
                error_pct = (diff / abs(actual_val)) * 100
                year_is_errors.append(abs(error_pct))
                lines.append(f"{label:<35} {forecast_val:>15,.0f} {actual_val:>15,.0f} {diff:>12,.0f} {error_pct:>9.1f}%")
            else:
                lines.append(f"{label:<35} {forecast_val:>15,.0f} {'N/A':>15} {'N/A':>12} {'N/A':>10}")
        
        if year_is_errors:
            lines.append("-" * 90)
            lines.append(f"{'Income Statement Avg Error:':<35} {sum(year_is_errors)/len(year_is_errors):>52.1f}%")
        
        # Balance Sheet comparison
        lines.append("")
        lines.append("BALANCE SHEET")
        lines.append(f"{'Item':<35} {'Forecast':>15} {'Actual':>15} {'Diff':>12} {'Error%':>10}")
        lines.append("-" * 90)
        
        for label, attr, csv_field in bs_compare_items:
            forecast_data = getattr(forecaster.balance_sheet, attr, [])
            forecast_val = forecast_data[i] if i < len(forecast_data) else 0
            actual_val = full_loader.get_value('balance', csv_field, year)
            
            if actual_val is not None and actual_val != 0:
                diff = forecast_val - actual_val
                error_pct = (diff / abs(actual_val)) * 100
                year_bs_errors.append(abs(error_pct))
                lines.append(f"{label:<35} {forecast_val:>15,.0f} {actual_val:>15,.0f} {diff:>12,.0f} {error_pct:>9.1f}%")
            else:
                lines.append(f"{label:<35} {forecast_val:>15,.0f} {'N/A':>15} {'N/A':>12} {'N/A':>10}")
        
        if year_bs_errors:
            lines.append("-" * 90)
            lines.append(f"{'Balance Sheet Avg Error:':<35} {sum(year_bs_errors)/len(year_bs_errors):>52.1f}%")
        
        # Store errors for summary
        all_errors = year_is_errors + year_bs_errors
        if all_errors:
            all_year_errors[year] = {
                'is': sum(year_is_errors)/len(year_is_errors) if year_is_errors else 0,
                'bs': sum(year_bs_errors)/len(year_bs_errors) if year_bs_errors else 0,
                'total': sum(all_errors)/len(all_errors)
            }
    
    # Summary across all years
    lines.append("")
    lines.append("=" * 120)
    lines.append("ERROR SUMMARY BY YEAR")
    lines.append("=" * 120)
    lines.append(f"{'Year':<10} {'Income Stmt':>15} {'Balance Sheet':>15} {'Overall':>15}")
    lines.append("-" * 60)
    
    for year, errors in all_year_errors.items():
        lines.append(f"{year:<10} {errors['is']:>14.1f}% {errors['bs']:>14.1f}% {errors['total']:>14.1f}%")
    
    if all_year_errors:
        avg_is = sum(e['is'] for e in all_year_errors.values()) / len(all_year_errors)
        avg_bs = sum(e['bs'] for e in all_year_errors.values()) / len(all_year_errors)
        avg_total = sum(e['total'] for e in all_year_errors.values()) / len(all_year_errors)
        lines.append("-" * 60)
        lines.append(f"{'Average':<10} {avg_is:>14.1f}% {avg_bs:>14.1f}% {avg_total:>14.1f}%")
    
    # Balance Sheet Check
    lines.append("")
    lines.append("=" * 100)
    lines.append("BALANCE SHEET CHECK")
    lines.append("=" * 100)
    lines.append(f"{'Year':<10} {'Total Assets':>15} {'Total L+E':>15} {'Difference':>15} {'Status':>12}")
    lines.append("-" * 100)
    
    for i in range(n_forecast_years + 1):
        year_label = str(int(base_year) + i)
        total_assets = forecaster.balance_sheet.total_assets[i]
        total_le = forecaster.balance_sheet.total_liabilities_equity[i]
        diff = total_assets - total_le
        status = "✓ Balanced" if abs(diff) < 1 else "✗ IMBALANCED"
        lines.append(f"{year_label:<10} {total_assets:>15,.0f} {total_le:>15,.0f} {diff:>15,.0f} {status:>12}")
    
    return lines


def view_config(company_name: str = None):
    """View company configuration(s)"""
    if company_name:
        # View specific company
        try:
            config = load_company_config(company_name)
        except Exception as e:
            print(f"Error loading config for {company_name}: {e}")
            return
        
        print(f"\n{'='*80}")
        print(f"CONFIGURATION: {config.company_name} ({config.company_ticker})")
        print(f"{'='*80}")
        
        print("\n📋 FORECAST SETTINGS:")
        print(f"   Base Year:          {config.base_year if config.base_year else '(Latest)'}")
        print(f"   Forecast Years:     {config.n_forecast_years}")
        print(f"   Input Years:        {config.n_input_years}")
        print(f"   Backtest Mode:      {config.is_backtest}")
        
        print("\n🔧 FIXED ASSUMPTIONS (Company Policy):")
        print(f"   LT Loan Years:      {config.lt_loan_years}")
        print(f"   ST Loan Years:      {config.st_loan_years}")
        print(f"   Debt Financing %:   {config.pct_financing_with_debt * 100:.0f}%")
        
        print("\n📝 OVERRIDES (null = use calculated):")
        overrides = {
            'Revenue Growth': config.revenue_growth_override,
            'Tax Rate': config.tax_rate_override,
            'Payout Ratio': config.payout_ratio_override,
            'COGS %': config.cogs_pct_override,
            'SG&A %': config.sga_pct_override,
            'CapEx %': config.capex_pct_override,
            'Cost of Debt': config.cost_of_debt_override,
        }
        for name, val in overrides.items():
            status = f"{val*100:.1f}%" if val is not None else "(calculated)"
            print(f"   {name:<18} {status}")
        
        print("\n📊 BOUNDS:")
        print(f"   Revenue Growth:     {config.min_revenue_growth*100:.1f}% to {config.max_revenue_growth*100:.1f}%")
        print(f"   Tax Rate:           {config.min_tax_rate*100:.1f}% to {config.max_tax_rate*100:.1f}%")
        print(f"   Depreciation Years: {config.min_depreciation_years:.0f} to {config.max_depreciation_years:.0f}")
        
    else:
        # View all companies
        companies = list_available_companies()
        
        if not companies:
            print("No company configurations found.")
            return
        
        print(f"\n{'='*80}")
        print("COMPANY CONFIGURATIONS")
        print(f"{'='*80}")
        
        print(f"\n{'Company':<20} {'Ticker':<8} {'Base':<8} {'FcstYrs':<8} {'LT Loan':<10} {'Debt%':<8}")
        print("-" * 80)
        
        for name in companies:
            try:
                c = load_company_config(name)
                base = str(c.base_year) if c.base_year else "Latest"
                print(f"{c.company_name:<20} {c.company_ticker:<8} {base:<8} {c.n_forecast_years:<8} "
                      f"{c.lt_loan_years:.0f} yrs     {c.pct_financing_with_debt*100:.0f}%")
            except Exception as e:
                print(f"{name:<20} Error: {e}")
        
        print(f"\nUse 'python run.py config <company>' for detailed view")


def list_companies():
    """List all available companies"""
    companies = list_available_companies()
    
    print(f"\n{'='*60}")
    print("AVAILABLE COMPANIES")
    print(f"{'='*60}")
    
    # Check data folders
    data_dir = os.path.join(project_root, "data")
    data_folders = [d for d in os.listdir(data_dir) 
                   if os.path.isdir(os.path.join(data_dir, d)) and not d.startswith('.')]
    
    print(f"\n{'Company Folder':<25} {'Has Config':<12} {'Status'}")
    print("-" * 60)
    
    for folder in sorted(data_folders):
        has_config = folder in companies
        config_status = "✓" if has_config else "✗"
        
        # Check data files
        folder_path = os.path.join(data_dir, folder)
        has_is = os.path.exists(os.path.join(folder_path, "income statement.csv"))
        has_bs = os.path.exists(os.path.join(folder_path, "balance sheet.csv"))
        has_cf = os.path.exists(os.path.join(folder_path, "cash flow.csv"))
        
        if has_is and has_bs and has_cf:
            data_status = "Complete"
        else:
            missing = []
            if not has_is: missing.append("IS")
            if not has_bs: missing.append("BS")
            if not has_cf: missing.append("CF")
            data_status = f"Missing: {', '.join(missing)}"
        
        print(f"{folder:<25} {config_status:<12} {data_status}")


def main():
    parser = argparse.ArgumentParser(
        description='Financial Forecasting Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py forecast ProcterGamble           # Standard forecast
  python run.py forecast ProcterGamble --full    # Full detailed output
  python run.py forecast ProcterGamble --base-year 2023  # Backtest (auto-detected)
  python run.py config                           # View all configs
  python run.py config ProcterGamble             # View specific config
  python run.py list                             # List companies

Note: Backtest mode is automatically enabled when forecast years have actual data.
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Forecast command
    forecast_parser = subparsers.add_parser('forecast', help='Run forecast (auto-detects backtest mode)')
    forecast_parser.add_argument('company', help='Company name')
    forecast_parser.add_argument('--base-year', type=int, help='Override base year')
    forecast_parser.add_argument('--years', type=int, help='Number of forecast years')
    forecast_parser.add_argument('--full', action='store_true', help='Full hierarchical output')
    forecast_parser.add_argument('--no-save', action='store_true', help='Do not save report')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='View configurations')
    config_parser.add_argument('company', nargs='?', help='Company name (optional)')
    
    # List command
    subparsers.add_parser('list', help='List available companies')
    
    args = parser.parse_args()
    
    if args.command == 'forecast':
        run_forecast(
            args.company,
            base_year=args.base_year,
            n_forecast_years=args.years,
            full_output=args.full,
            save_report=not args.no_save
        )
    elif args.command == 'config':
        view_config(args.company)
    elif args.command == 'list':
        list_companies()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
