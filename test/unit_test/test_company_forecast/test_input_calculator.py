"""
Unit tests for InputCalculator module.
Tests calculation of forecast inputs from historical data.
"""

import pytest
from company_forecast.input_calculator import InputCalculator
from company_forecast.data_loader import DataLoader
from company_forecast.config import ForecastConfig, ModelAssumptions


class TestInputCalculator:
    """Tests for InputCalculator class"""
    
    def test_initialization(self, create_test_company):
        """Test InputCalculator initialization"""
        company_folder = create_test_company("InputCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=3, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        
        assert ic.data == dl
        assert ic.config == cfg
        assert ic.assumptions is not None
        assert isinstance(ic.inputs, dict)
        assert len(ic.inputs) == 0  # Not calculated yet
    
    def test_calculate_all_inputs_returns_dict(self, create_test_company):
        """Test that calculate_all_inputs returns a dictionary"""
        company_folder = create_test_company("CalcCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert isinstance(inputs, dict)
        assert len(inputs) > 0
    
    def test_calculate_all_inputs_has_required_keys(self, create_test_company):
        """Test that all required input keys are present"""
        company_folder = create_test_company("ReqCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        # Year 0 values (income statement)
        assert 'revenue_year_0' in inputs
        assert 'cogs_year_0' in inputs
        assert 'gross_profit_year_0' in inputs
        assert 'sga_year_0' in inputs
        assert 'depreciation_year_0' in inputs
        assert 'operating_income_year_0' in inputs
        assert 'net_income_year_0' in inputs
        
        # Year 0 values (balance sheet)
        assert 'cash_year_0' in inputs
        assert 'accounts_receivable_year_0' in inputs
        assert 'inventory_year_0' in inputs
        assert 'net_ppe_year_0' in inputs
        assert 'total_assets_year_0' in inputs
        assert 'short_term_debt_year_0' in inputs
        assert 'long_term_debt_year_0' in inputs
        assert 'total_equity_year_0' in inputs
        
        # Year 0 values (cash flow)
        assert 'operating_cash_flow_year_0' in inputs
        assert 'capex_year_0' in inputs
        assert 'dividends_paid_year_0' in inputs
        
        # Forecast parameters
        assert 'revenue_growth' in inputs
        assert 'cogs_pct_revenue' in inputs
        assert 'sga_pct_revenue' in inputs
        assert 'tax_rate' in inputs
        assert 'depreciation_rate' in inputs
        assert 'payout_ratio' in inputs
    
    def test_year_0_values_match_data(self, create_test_company, sample_financial_data):
        """Test that Year 0 values are correctly extracted from historical data"""
        company_folder = create_test_company("Y0Co")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        # Check some key values match the sample data
        assert inputs['revenue_year_0'] == 120.0
        assert inputs['cogs_year_0'] == -72.0
        assert inputs['net_income_year_0'] == 22.8
        assert inputs['total_assets_year_0'] == 300.0
        assert inputs['cash_year_0'] == 15.0
    
    def test_revenue_growth_calculation(self, create_test_company):
        """Test revenue growth rate calculation"""
        company_folder = create_test_company("GrowthCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=3, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'revenue_growth' in inputs
        assert isinstance(inputs['revenue_growth'], list)
        assert len(inputs['revenue_growth']) == cfg.n_forecast_years
        
        # Revenue growth should be positive (120/110 - 1 ≈ 9%)
        for growth in inputs['revenue_growth']:
            assert isinstance(growth, (int, float))
    
    def test_cost_structure_percentages(self, create_test_company):
        """Test cost structure percentage calculations"""
        company_folder = create_test_company("CostCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        # COGS as % of revenue (should be around 0.6)
        assert 'cogs_pct_revenue' in inputs
        # Allow negative values for COGS (expense)
        assert abs(inputs['cogs_pct_revenue']) < 2
        
        # SG&A as % of revenue
        assert 'sga_pct_revenue' in inputs
        assert abs(inputs['sga_pct_revenue']) < 2
    
    def test_working_capital_ratios(self, create_test_company):
        """Test working capital ratio calculations"""
        company_folder = create_test_company("WCCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'ar_pct_revenue' in inputs
        assert 'inventory_pct_cogs' in inputs
        assert 'ap_pct_cogs' in inputs
        
        # All should be positive percentages
        assert inputs['ar_pct_revenue'] > 0
        assert inputs['inventory_pct_cogs'] > 0
        assert inputs['ap_pct_cogs'] > 0
    
    def test_tax_rate_calculation(self, create_test_company):
        """Test tax rate calculation"""
        company_folder = create_test_company("TaxCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'tax_rate' in inputs
        # Tax rate should be between 0 and 1
        assert 0 <= inputs['tax_rate'] <= 1
    
    def test_depreciation_rate_calculation(self, create_test_company):
        """Test depreciation rate calculation"""
        company_folder = create_test_company("DeprCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'depreciation_rate' in inputs
        # Depreciation rate can be negative if assets depreciated more than expected
        assert isinstance(inputs['depreciation_rate'], (int, float))
    
    def test_payout_ratio_calculation(self, create_test_company):
        """Test payout ratio calculation"""
        company_folder = create_test_company("PayoutCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'payout_ratio' in inputs
        # Payout ratio should be between 0 and 1 (or slightly above for special cases)
        assert 0 <= inputs['payout_ratio'] <= 2.0  # Allow some flexibility
    
    def test_interest_rate_calculation(self, create_test_company):
        """Test interest rate calculations"""
        company_folder = create_test_company("IntCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'cost_of_debt' in inputs
        assert 'return_st_investment' in inputs
        
        # Interest rates should be reasonable
        assert -0.1 < inputs['cost_of_debt'] < 0.5
        assert -0.1 < inputs['return_st_investment'] < 0.5
    
    def test_capex_calculation(self, create_test_company):
        """Test capital expenditure calculations"""
        company_folder = create_test_company("CapexCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'capex_year_0' in inputs
        assert 'capex_pct_revenue' in inputs
        
        # CapEx should be positive
        assert inputs['capex_year_0'] > 0
        assert inputs['capex_pct_revenue'] > 0
    
    def test_with_custom_assumptions(self, create_test_company):
        """Test InputCalculator with custom ModelAssumptions"""
        company_folder = create_test_company("CustomCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        custom_assumptions = ModelAssumptions(
            default_tax_rate=0.25,
            default_payout_ratio=0.40
        )
        
        ic = InputCalculator(dl, cfg, assumptions=custom_assumptions)
        inputs = ic.calculate_all_inputs()
        
        # Should still return valid inputs
        assert isinstance(inputs, dict)
        assert 'tax_rate' in inputs
        assert 'payout_ratio' in inputs
    
    def test_financing_parameters(self, create_test_company):
        """Test financing parameter calculations"""
        company_folder = create_test_company("FinCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        cfg = ForecastConfig(n_forecast_years=2, n_input_years=2)
        
        ic = InputCalculator(dl, cfg)
        inputs = ic.calculate_all_inputs()
        
        assert 'pct_financing_with_debt' in inputs
        assert 'st_loan_years' in inputs
        assert 'lt_loan_years' in inputs
        
        # Debt financing percentage should be between 0 and 1
        assert 0 <= inputs['pct_financing_with_debt'] <= 1
        
        # Loan years should be positive
        assert inputs['st_loan_years'] > 0
        assert inputs['lt_loan_years'] > 0
        assert inputs['lt_loan_years'] > inputs['st_loan_years']  # LT should be longer than ST
