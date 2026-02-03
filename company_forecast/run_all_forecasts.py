#!/usr/bin/env python3
"""
Run forecasts for all available companies.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from company_forecast import CompanyForecaster


def main():
    companies = ["ProcterGamble", "CocaCola", "Costco", "McDonalds"]
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    results = {}
    
    for company in companies:
        print(f"\n{'='*80}")
        print(f"FORECASTING: {company}")
        print(f"{'='*80}")
        
        data_folder = os.path.join(base_path, "data", company)
        
        if not os.path.exists(data_folder):
            print(f"  ✗ Data folder not found: {data_folder}")
            results[company] = "Failed - No data"
            continue
        
        try:
            forecaster = CompanyForecaster(
                company_folder=data_folder,
                n_forecast_years=4
            )
            
            forecaster.run_forecast()
            forecaster.print_summary()
            
            # Save to output folder
            output_folder = os.path.join(base_path, "output")
            os.makedirs(output_folder, exist_ok=True)
            output_file = os.path.join(output_folder, f"{company}_forecast.xlsx")
            forecaster.save_to_excel(output_file)
            
            # Check if balance sheet balances
            max_imbalance = max(abs(v) for v in forecaster.balance_sheet.balance_check)
            if max_imbalance < 1:  # Less than $1 million imbalance
                results[company] = f"Success - Balanced (max imbalance: ${max_imbalance:,.0f})"
            else:
                results[company] = f"Warning - Imbalanced (max imbalance: ${max_imbalance:,.0f})"
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results[company] = f"Failed - {str(e)}"
    
    # Print summary
    print(f"\n{'='*80}")
    print("FORECAST SUMMARY")
    print(f"{'='*80}")
    for company, status in results.items():
        print(f"  {company}: {status}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
