"""
Main script to run the financial forecasting model.
"""

from forecast_model.forecaster import Forecaster


def main():
    """Run the financial forecast"""
    
    # Create forecaster instance and run forecast
    forecaster = Forecaster()
    forecaster.run_forecast()
    
    # Print summary
    print("\n" + "=" * 80)
    print("FORECAST SUMMARY")
    print("=" * 80)
    forecaster.print_summary()
    
    # Optionally save results to Excel
    # forecaster.save_to_excel('forecast_results.xlsx')
    # print("\nResults saved to forecast_results.xlsx")


if __name__ == "__main__":
    main()
