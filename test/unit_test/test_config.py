import pytest
from company_forecast.config import ForecastConfig


def test_forecast_config_properties():
    cfg = ForecastConfig(n_forecast_years=3, base_year=2020)
    assert cfg.n_forecast_years == 3
    assert cfg.forecast_years == [1, 2, 3]
    assert cfg.all_years == [0, 1, 2, 3]
    assert cfg.year_labels == ["2020", "2021", "2022", "2023"]
