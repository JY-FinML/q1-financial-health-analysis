from company_forecast.intermediate import IntermediateCalculations
from company_forecast.config import ForecastConfig


def test_intermediate_revenue_and_cogs():
    # minimal inputs required by IntermediateCalculations
    inputs = {
        'revenue_year_0': 100.0,
        'cogs_year_0': 60.0,
        'gross_profit_year_0': 40.0,
        'sga_year_0': 10.0,
        'operating_income_year_0': 30.0,
        'depreciation_year_0': 5.0,
        'accumulated_depreciation_year_0': 20.0,
        'net_ppe_year_0': 100.0,
        'gross_ppe_year_0': 120.0,
        'capex_year_0': 4.0,
        'accounts_receivable_year_0': 8.0,
        'inventory_year_0': 5.0,
        'accounts_payable_year_0': 6.0,
        'cash_year_0': 3.0,
        'cost_of_debt': 0.05,
        'return_st_investment': 0.03,
        'cogs_pct_revenue': 0.6,
        'sga_pct_revenue': 0.1,
        'capex_pct_revenue': 0.04,
        'depreciation_rate': 0.05,
        'ar_pct_revenue': 0.08,
        'inventory_pct_cogs': 0.05,
        'ap_pct_cogs': 0.1,
        'min_cash_pct_revenue': 0.04,
        'goodwill_year_0': 0.0,
        'intangible_assets_year_0': 0.0,
        'revenue_growth': [0.03, 0.03],
    }
    cfg = ForecastConfig(n_forecast_years=2)
    ic = IntermediateCalculations(inputs, cfg)
    ic.calculate_all()
    # After one year, revenue should increase based on revenue_growth default absent (KeyError avoided)
    assert len(ic.revenue) == cfg.n_forecast_years + 1
    assert len(ic.cogs) == cfg.n_forecast_years + 1
