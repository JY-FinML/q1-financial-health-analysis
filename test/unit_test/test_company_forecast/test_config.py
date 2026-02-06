"""
Unit tests for config module.
Tests ForecastConfig and ModelAssumptions dataclasses.
"""

import pytest
from company_forecast.config import ForecastConfig, ModelAssumptions


class TestForecastConfig:
    """Tests for ForecastConfig dataclass"""
    
    def test_default_initialization(self):
        """Test ForecastConfig with default values"""
        cfg = ForecastConfig()
        assert cfg.n_forecast_years == 4
        assert cfg.n_input_years == 3
        assert cfg.base_year == 2025
    
    def test_custom_initialization(self):
        """Test ForecastConfig with custom values"""
        cfg = ForecastConfig(n_forecast_years=3, n_input_years=2, base_year=2020)
        assert cfg.n_forecast_years == 3
        assert cfg.n_input_years == 2
        assert cfg.base_year == 2020
    
    def test_forecast_years_property(self):
        """Test forecast_years property returns correct list"""
        cfg = ForecastConfig(n_forecast_years=3)
        assert cfg.forecast_years == [1, 2, 3]
        
        cfg = ForecastConfig(n_forecast_years=5)
        assert cfg.forecast_years == [1, 2, 3, 4, 5]
    
    def test_all_years_property(self):
        """Test all_years includes Year 0"""
        cfg = ForecastConfig(n_forecast_years=3)
        assert cfg.all_years == [0, 1, 2, 3]
        assert len(cfg.all_years) == cfg.n_forecast_years + 1
    
    def test_year_labels_property(self):
        """Test year_labels generates correct string labels"""
        cfg = ForecastConfig(n_forecast_years=3, base_year=2020)
        assert cfg.year_labels == ["2020", "2021", "2022", "2023"]
        
        cfg = ForecastConfig(n_forecast_years=2, base_year=2023)
        assert cfg.year_labels == ["2023", "2024", "2025"]
    
    def test_year_labels_length(self):
        """Test year_labels has correct length"""
        cfg = ForecastConfig(n_forecast_years=4, base_year=2020)
        assert len(cfg.year_labels) == cfg.n_forecast_years + 1  # Includes Year 0


class TestModelAssumptions:
    """Tests for ModelAssumptions dataclass"""
    
    def test_default_initialization(self):
        """Test ModelAssumptions with default values"""
        assumptions = ModelAssumptions()
        
        # Depreciation
        assert assumptions.default_depreciation_years == 10.0
        
        # Tax
        assert assumptions.default_tax_rate == 0.21
        
        # Debt parameters
        assert assumptions.st_loan_years == 1.0
        assert assumptions.lt_loan_years == 10.0
        
        # Financing mix
        assert assumptions.pct_financing_with_debt == 0.70
        
        # Interest rates
        assert assumptions.real_interest_rate == 0.02
        assert assumptions.risk_premium_debt == 0.04
        assert assumptions.risk_premium_st_investment == -0.01
        
        # Payout
        assert assumptions.default_payout_ratio == 0.50
        
        # Working capital
        assert assumptions.default_ar_pct == 0.08
        assert assumptions.default_inventory_pct == 0.05
        assert assumptions.default_ap_pct == 0.10
        
        # Cash requirements
        assert assumptions.min_cash_pct_revenue == 0.04
        
        # Growth
        assert assumptions.default_revenue_growth == 0.03
        assert assumptions.default_inflation_rate == 0.025
    
    def test_custom_initialization(self):
        """Test ModelAssumptions with custom values"""
        assumptions = ModelAssumptions(
            default_tax_rate=0.25,
            pct_financing_with_debt=0.60,
            default_revenue_growth=0.05
        )
        
        assert assumptions.default_tax_rate == 0.25
        assert assumptions.pct_financing_with_debt == 0.60
        assert assumptions.default_revenue_growth == 0.05
        
        # Check other defaults are unchanged
        assert assumptions.default_depreciation_years == 10.0
        assert assumptions.st_loan_years == 1.0
    
    def test_all_assumptions_are_positive_or_zero(self):
        """Test that percentage assumptions are in valid range"""
        assumptions = ModelAssumptions()
        
        # These should all be positive
        assert assumptions.default_depreciation_years > 0
        assert assumptions.st_loan_years > 0
        assert assumptions.lt_loan_years > 0
        
        # Tax rate should be between 0 and 1
        assert 0 <= assumptions.default_tax_rate <= 1
        
        # Payout ratio should be between 0 and 1
        assert 0 <= assumptions.default_payout_ratio <= 1
        
        # Financing percentage should be between 0 and 1
        assert 0 <= assumptions.pct_financing_with_debt <= 1
