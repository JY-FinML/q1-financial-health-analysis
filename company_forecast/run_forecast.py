#!/usr/bin/env python3
"""
Run Company Financial Forecast

This script runs the financial forecasting model for a specified company
using historical data to predict future financial statements.

Usage:
    python run_forecast.py [company_name]
    
    company_name: Name of company folder in data/ directory
                  Options: ProcterGamble, CocaCola, Costco, McDonalds
                  Default: ProcterGamble
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from company_forecast import CompanyForecaster


def main():
    # Get company name from command line or use default
    if len(sys.argv) > 1:
        company_name = sys.argv[1]
    else:
        company_name = "ProcterGamble"
    
    # Available companies
    available_companies = ["ProcterGamble", "CocaCola", "Costco", "McDonalds"]
    
    if company_name not in available_companies:
        print(f"Error: Unknown company '{company_name}'")
        print(f"Available companies: {', '.join(available_companies)}")
        return
    
    # Path to company data
    data_folder = os.path.join(os.path.dirname(__file__), "data", company_name)
    
    if not os.path.exists(data_folder):
        print(f"Error: Data folder not found: {data_folder}")
        return
    
    # Create and run forecaster
    print(f"\n{'='*80}")
    print(f"Running forecast for: {company_name}")
    print(f"{'='*80}\n")
    
    try:
        forecaster = CompanyForecaster(
            company_folder=data_folder,
            n_forecast_years=4
        )
        
        # Run the forecast
        forecaster.run_forecast()
        
        # Print summary
        forecaster.print_summary()
        
        # Save to Excel
        output_file = forecaster.save_to_excel()
        
        print(f"\n{'='*80}")
        print(f"Forecast complete for {company_name}!")
        print(f"Results saved to: {output_file}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"Error running forecast: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
