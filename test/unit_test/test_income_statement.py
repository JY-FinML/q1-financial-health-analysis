import pytest
from company_forecast.income_statement import IncomeStatement
from company_forecast.config import ForecastConfig


def test_income_statement_interest_and_net_income():
    # Minimal inputs and stubs
    inputs = {
        'revenue_year_0': 100,
        'cogs_year_0': 60,
        'gross_profit_year_0': 40,
        'sga_year_0': 10,
        'depreciation_year_0': 5,
        'operating_income_year_0': 25,
        'interest_expense_year_0': 1,
        'pretax_income_year_0': 24,
        'tax_provision_year_0': 4,
        'net_income_year_0': 20,
        'dividends_paid_year_0': 2,
        'retained_earnings_year_0': 100,
        'tax_rate': 0.2,
        'payout_ratio': 0.5,
    }
    cfg = ForecastConfig(n_forecast_years=2)

    # Intermediate stub with forecasted values
    class IntStub:
        revenue = [100, 110, 121]
        cogs = [60, 66, 72.6]
        gross_profit = [40, 44, 48.4]
        sga_expenses = [10, 11, 12.1]
        depreciation = [5, 5, 5]
        cost_of_debt = [0.05, 0.05]
        return_st_investment = [0.02, 0.02]

    # CashBudget stub for st_investment
    class CBStub:
        st_investment = [0, 0, 0]

    # DebtSchedule stub
    class DSStub:
        st_ending_balance = [0, 100, 50]
        lt_ending_balance = [0, 200, 180]

    intermediate = IntStub()
    cb = CBStub()
    ds = DSStub()

    is_obj = IncomeStatement(inputs, cfg, intermediate)
    is_obj.calculate_year(1, cb, ds)
    # After calculation, interest expense should be > = 0
    assert is_obj.interest_expense[1] >= 0
    assert is_obj.net_income[1] == pytest.approx(is_obj.ebt[1] - is_obj.income_taxes[1])
