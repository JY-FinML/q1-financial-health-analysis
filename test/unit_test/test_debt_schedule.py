from company_forecast.debt_schedule import DebtSchedule
from company_forecast.config import ForecastConfig


def test_debt_schedule_initialize_and_payments():
    inputs = {'st_loan_years': 1.0, 'lt_loan_years': 10.0}
    cfg = ForecastConfig(n_forecast_years=3)
    ds = DebtSchedule(inputs, cfg)

    ds.initialize_year_0(100, 1000)
    assert ds.st_ending_balance[0] == 100
    assert ds.lt_ending_balance[0] == 1000

    # Add a new LT loan in year 1 and check principal payment calculation
    ds.update_lt_debt(1, 500)
    total_payment = ds.get_total_lt_principal_payment(1)
    assert total_payment >= 0

    # Update ST debt: repay principal and add new loan
    ds.update_st_debt(1, new_loan=50, principal_payment=100)
    assert ds.st_ending_balance[1] >= 0
