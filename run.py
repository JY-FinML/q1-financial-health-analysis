#!/usr/bin/env python3
"""
Main Entry Point for Financial Forecasting

Unified command-line interface for all forecast operations.

Usage:
    python run.py forecast ProcterGamble           # Standard forecast (latest year as base)
    python run.py forecast ProcterGamble --full    # Full detailed output
    python run.py backtest ProcterGamble           # Backtest with config settings
    python run.py config                           # View all company configs
    python run.py config ProcterGamble             # View specific company config
    python run.py list                             # List available companies
    
Options:
    --base-year YEAR    Override base year (default: from config or latest)
    --years N           Number of years to forecast (default: from config or 2)
    --full              Show full hierarchical output
    --no-save           Don't save report to file
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
    lines.append("")
    
    if full_output:
        # Full hierarchical output
        lines.extend(_generate_full_output(forecaster, actual_base_year, forecast_years, n_forecast_years))
    else:
        # Compact output
        lines.extend(_generate_compact_output(forecaster, actual_base_year, forecast_years, n_forecast_years))
    
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
        filename = f"{mode_str}_{company_name}_{timestamp}.txt"
        with open(os.path.join(project_root, filename), 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {filename}")
    
    return report


def _generate_compact_output(forecaster, base_year, forecast_years, n_forecast_years):
    """Generate compact forecast output"""
    lines = []
    
    # Header
    header = f"{'Item':<30}" + f"{'Y0 (' + base_year + ')':>15}"
    for i, y in enumerate(forecast_years, 1):
        header += f"{'Y' + str(i) + ' (' + y + ')':>15}"
    
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
        data = getattr(forecaster.income_statement, attr, [])
        row = f"{label:<30}"
        for i in range(n_forecast_years + 1):
            val = data[i] if i < len(data) else 0
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
        ('Total Liab & Equity', 'total_liabilities_equity'),
        ('Balance Check', 'balance_check'),
    ]
    
    for label, attr in bs_items:
        data = getattr(forecaster.balance_sheet, attr, [])
        row = f"{label:<30}"
        for i in range(n_forecast_years + 1):
            val = data[i] if i < len(data) else 0
            row += f"{val:>15,.0f}"
        lines.append(row)
    
    return lines


def _generate_full_output(forecaster, base_year, forecast_years, n_forecast_years):
    """Generate full hierarchical forecast output"""
    lines = []
    
    # Header
    header = f"{'Item':<45}" + f"{'Y0 (' + base_year + ')':>15}"
    for i, y in enumerate(forecast_years, 1):
        header += f"{'Y' + str(i) + ' (' + y + ')':>15}"
    
    # Income Statement
    lines.append("=" * 120)
    lines.append("INCOME STATEMENT (Full Detail)")
    lines.append("=" * 120)
    lines.append(header)
    lines.append("-" * 120)
    
    is_items = [
        ("Revenue", forecaster.income_statement.revenue),
        ("  Cost of Revenue", forecaster.income_statement.cogs),
        ("Gross Profit", forecaster.income_statement.gross_profit),
        ("  SG&A Expense", forecaster.income_statement.sga_expenses),
        ("  Depreciation", forecaster.income_statement.depreciation),
        ("Operating Income", forecaster.income_statement.operating_income),
        ("  Interest Expense", forecaster.income_statement.interest_expense),
        ("  Interest Income (ST Inv)", forecaster.income_statement.interest_income),
        ("Pretax Income (EBT)", forecaster.income_statement.ebt),
        ("  Tax Expense", forecaster.income_statement.income_taxes),
        ("Net Income", forecaster.income_statement.net_income),
        ("  Dividends", forecaster.income_statement.dividends),
    ]
    
    for label, values in is_items:
        row = f"{label:<45}"
        for i in range(n_forecast_years + 1):
            val = values[i] if i < len(values) else 0
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
        ("ASSETS", None),
        ("  Cash & ST Investments", forecaster.balance_sheet.cash),
        ("  Accounts Receivable", forecaster.balance_sheet.accounts_receivable),
        ("  Inventory", forecaster.balance_sheet.inventory),
        ("  Other Current Assets", forecaster.balance_sheet.other_current_assets),
        ("Current Assets", forecaster.balance_sheet.current_assets),
        ("  Net PP&E", forecaster.balance_sheet.net_ppe),
        ("  Goodwill", forecaster.balance_sheet.goodwill),
        ("  Intangible Assets", forecaster.balance_sheet.intangible_assets),
        ("  Other Non-Current Assets", forecaster.balance_sheet.other_non_current_assets),
        ("Total Non-Current Assets", forecaster.balance_sheet.total_non_current_assets),
        ("Total Assets", forecaster.balance_sheet.total_assets),
        ("", None),
        ("LIABILITIES", None),
        ("  Accounts Payable", forecaster.balance_sheet.accounts_payable),
        ("  Short-term Debt", forecaster.balance_sheet.short_term_debt),
        ("  Other Current Liabilities", forecaster.balance_sheet.other_current_liabilities),
        ("Current Liabilities", forecaster.balance_sheet.current_liabilities),
        ("  Long-term Debt", forecaster.balance_sheet.long_term_debt),
        ("  Other Non-Current Liabilities", forecaster.balance_sheet.other_non_current_liabilities),
        ("Total Non-Current Liabilities", forecaster.balance_sheet.total_non_current_liabilities),
        ("Total Liabilities", forecaster.balance_sheet.total_liabilities),
        ("", None),
        ("EQUITY", None),
        ("  Retained Earnings", forecaster.balance_sheet.retained_earnings),
        ("  Other Equity", forecaster.balance_sheet.other_equity),
        ("Total Equity", forecaster.balance_sheet.total_equity),
        ("", None),
        ("Total Liab & Equity", forecaster.balance_sheet.total_liabilities_equity),
        ("Balance Check (A - L - E)", forecaster.balance_sheet.balance_check),
    ]
    
    for label, values in bs_items:
        if values is None:
            if label:
                lines.append(f"{label}")
            else:
                lines.append("")
        else:
            row = f"{label:<45}"
            for i in range(n_forecast_years + 1):
                val = values[i] if i < len(values) else 0
                row += f"{val:>15,.0f}"
            lines.append(row)
    
    return lines


def _generate_backtest_comparison(forecaster, company_folder, base_year, forecast_years, n_forecast_years):
    """Generate backtest comparison with actual data"""
    lines = []
    
    # Load full data
    full_loader = DataLoader(company_folder)
    full_loader.load_all()
    
    lines.append("=" * 100)
    lines.append("BACKTEST COMPARISON (Forecast vs Actual)")
    lines.append("=" * 100)
    lines.append(f"{'Item':<25} {'Year':<8} {'Forecast':>12} {'Actual':>12} {'Diff':>10} {'Error%':>8}")
    lines.append("-" * 100)
    
    compare_items = [
        ('Revenue', 'revenue', 'income', 'Total Revenue'),
        ('Net Income', 'net_income', 'income', 'Net Income'),
        ('Total Assets', 'total_assets', 'balance', 'Total Assets'),
        ('Total Equity', 'total_equity', 'balance', 'Stockholders Equity'),
    ]
    
    errors = []
    for label, attr, stmt, csv_field in compare_items:
        forecast_data = getattr(
            forecaster.income_statement if stmt == 'income' else forecaster.balance_sheet, 
            attr, []
        )
        for i, year in enumerate(forecast_years, 1):
            forecast_val = forecast_data[i] if i < len(forecast_data) else 0
            actual_val = full_loader.get_value(stmt, csv_field, year)
            
            if actual_val is not None and actual_val != 0:
                diff = forecast_val - actual_val
                error_pct = (diff / abs(actual_val)) * 100
                errors.append(abs(error_pct))
                lines.append(f"{label:<25} {year:<8} {forecast_val:>12,.0f} {actual_val:>12,.0f} {diff:>10,.0f} {error_pct:>7.1f}%")
    
    if errors:
        lines.append("-" * 100)
        lines.append(f"Average Absolute Error: {sum(errors)/len(errors):.1f}%")
    
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
  python run.py backtest ProcterGamble           # Run backtest
  python run.py config                           # View all configs
  python run.py config ProcterGamble             # View specific config
  python run.py list                             # List companies
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Forecast command
    forecast_parser = subparsers.add_parser('forecast', help='Run forecast')
    forecast_parser.add_argument('company', help='Company name')
    forecast_parser.add_argument('--base-year', type=int, help='Override base year')
    forecast_parser.add_argument('--years', type=int, help='Number of forecast years')
    forecast_parser.add_argument('--full', action='store_true', help='Full hierarchical output')
    forecast_parser.add_argument('--no-save', action='store_true', help='Do not save report')
    
    # Backtest command (alias for forecast with older base year)
    backtest_parser = subparsers.add_parser('backtest', help='Run backtest')
    backtest_parser.add_argument('company', help='Company name')
    backtest_parser.add_argument('--base-year', type=int, help='Override base year')
    backtest_parser.add_argument('--years', type=int, help='Number of forecast years')
    backtest_parser.add_argument('--full', action='store_true', help='Full hierarchical output')
    backtest_parser.add_argument('--no-save', action='store_true', help='Do not save report')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='View configurations')
    config_parser.add_argument('company', nargs='?', help='Company name (optional)')
    
    # List command
    subparsers.add_parser('list', help='List available companies')
    
    args = parser.parse_args()
    
    if args.command == 'forecast' or args.command == 'backtest':
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
