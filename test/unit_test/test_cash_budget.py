from company_forecast.cash_budget import CashBudget
from company_forecast.debt_schedule import DebtSchedule
from company_forecast.config import ForecastConfig


def test_cash_budget_year_0_initialization():
    inputs = {
        'operating_cash_flow_year_0': 10,
        'capex_year_0': 2,
        'dividends_paid_year_0': 1,
        'stock_repurchase_year_0': 0,
        'cash_year_0': 50,
        'short_term_debt_year_0': 5,
        'long_term_debt_year_0': 20,
    }
    cfg = ForecastConfig(n_forecast_years=2)
    # minimal intermediate stub
    class Stub:
        depreciation = [0, 0]
    intermediate = Stub()

    cb = CashBudget(inputs, cfg, intermediate)
    ds = DebtSchedule(inputs, cfg)
    st0, lt0, eq0 = cb.calculate_year_0(ds)
    assert st0 == inputs.get('short_term_debt_year_0', 0) or st0 == 0
    assert cb.cumulated_ncb[0] == inputs['cash_year_0']
