"""
Unit tests for IntermediateCalculations module.
Tests calculation of intermediate forecast values.
"""

import pytest
from company_forecast.intermediate import IntermediateCalculations
from company_forecast.config import ForecastConfig


class TestIntermediateCalculations:
    """Tests for IntermediateCalculations class"""
    
    def test_initialization(self, minimal_inputs, forecast_config):
        """Test IntermediateCalculations initialization"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        
        # Check Year 0 values are set from inputs
        assert ic.revenue[0] == minimal_inputs['revenue_year_0']
        assert ic.cogs[0] == minimal_inputs['cogs_year_0']
        assert ic.depreciation[0] == minimal_inputs['depreciation_year_0']
        assert ic.net_ppe[0] == minimal_inputs['net_ppe_year_0']
        
        # Check lists are initialized with Year 0
        assert len(ic.revenue) == 1
        assert len(ic.cogs) == 1
        assert len(ic.depreciation) == 1
    
    def test_calculate_all_completes(self, minimal_inputs, forecast_config):
        """Test that calculate_all runs without errors"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        
        # Should not raise exception
        ic.calculate_all()
        
        # All arrays should now have forecast_years + 1 elements (Year 0 + forecasts)
        expected_length = forecast_config.n_forecast_years + 1
        assert len(ic.revenue) == expected_length
        assert len(ic.cogs) == expected_length
        assert len(ic.depreciation) == expected_length
        assert len(ic.net_ppe) == expected_length
    
    def test_revenue_forecast_growth(self, minimal_inputs, forecast_config):
        """Test revenue forecasting with growth rate"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        # Revenue should grow by specified rate
        growth_rate = minimal_inputs['revenue_growth'][0]  # 0.05
        year_0_revenue = minimal_inputs['revenue_year_0']  # 100.0
        
        expected_year_1_revenue = year_0_revenue * (1 + growth_rate)
        assert ic.revenue[1] == pytest.approx(expected_year_1_revenue, rel=1e-6)
        
        # Year 2 should compound
        expected_year_2_revenue = expected_year_1_revenue * (1 + growth_rate)
        assert ic.revenue[2] == pytest.approx(expected_year_2_revenue, rel=1e-6)
    
    def test_cogs_calculation(self, minimal_inputs, forecast_config):
        """Test COGS calculation as percentage of revenue"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        cogs_pct = minimal_inputs['cogs_pct_revenue']  # 0.60
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_cogs = ic.revenue[year] * cogs_pct
            assert ic.cogs[year] == pytest.approx(expected_cogs, rel=1e-6)
    
    def test_gross_profit_calculation(self, minimal_inputs, forecast_config):
        """Test gross profit = revenue - COGS"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_gross_profit = ic.revenue[year] - ic.cogs[year]
            assert ic.gross_profit[year] == pytest.approx(expected_gross_profit, rel=1e-6)
    
    def test_sga_expenses_calculation(self, minimal_inputs, forecast_config):
        """Test SG&A calculation as percentage of revenue"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        sga_pct = minimal_inputs['sga_pct_revenue']  # 0.10
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_sga = ic.revenue[year] * sga_pct
            assert ic.sga_expenses[year] == pytest.approx(expected_sga, rel=1e-6)
    
    def test_capex_calculation(self, minimal_inputs, forecast_config):
        """Test CapEx calculation as percentage of revenue"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        capex_pct = minimal_inputs['capex_pct_revenue']  # 0.10
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_capex = ic.revenue[year] * capex_pct
            assert ic.capex[year] == pytest.approx(expected_capex, rel=1e-6)
    
    def test_depreciation_calculation(self, minimal_inputs, forecast_config):
        """Test depreciation based on beginning net PPE"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        depr_rate = minimal_inputs['depreciation_rate']  # 0.05
        
        # Year 1 depreciation = Year 0 net PPE * depreciation rate
        expected_depr_1 = minimal_inputs['net_ppe_year_0'] * depr_rate
        assert ic.depreciation[1] == pytest.approx(expected_depr_1, rel=1e-6)
    
    def test_net_ppe_calculation(self, minimal_inputs, forecast_config):
        """Test Net PPE = Previous Net PPE + CapEx - Depreciation"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_net_ppe = (ic.net_ppe[year - 1] + 
                              ic.capex[year] - 
                              ic.depreciation[year])
            assert ic.net_ppe[year] == pytest.approx(expected_net_ppe, rel=1e-6)
    
    def test_gross_ppe_accumulation(self, minimal_inputs, forecast_config):
        """Test Gross PPE accumulates CapEx"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_gross_ppe = ic.gross_ppe[year - 1] + ic.capex[year]
            assert ic.gross_ppe[year] == pytest.approx(expected_gross_ppe, rel=1e-6)
    
    def test_cumulated_depreciation(self, minimal_inputs, forecast_config):
        """Test cumulated depreciation accumulates over years"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_cum_depr = (ic.cumulated_depreciation[year - 1] + 
                                ic.depreciation[year])
            assert ic.cumulated_depreciation[year] == pytest.approx(expected_cum_depr, rel=1e-6)
    
    def test_accounts_receivable_calculation(self, minimal_inputs, forecast_config):
        """Test AR as percentage of revenue"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        ar_pct = minimal_inputs['ar_pct_revenue']  # 0.08
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_ar = ic.revenue[year] * ar_pct
            assert ic.accounts_receivable[year] == pytest.approx(expected_ar, rel=1e-6)
    
    def test_inventory_calculation(self, minimal_inputs, forecast_config):
        """Test inventory as percentage of COGS"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        inv_pct = minimal_inputs['inventory_pct_cogs']  # 0.10
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_inv = ic.cogs[year] * inv_pct
            assert ic.inventory[year] == pytest.approx(expected_inv, rel=1e-6)
    
    def test_accounts_payable_calculation(self, minimal_inputs, forecast_config):
        """Test AP as percentage of COGS"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        ap_pct = minimal_inputs['ap_pct_cogs']  # 0.08
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_ap = ic.cogs[year] * ap_pct
            assert ic.accounts_payable[year] == pytest.approx(expected_ap, rel=1e-6)
    
    def test_working_capital_changes(self, minimal_inputs, forecast_config):
        """Test working capital change calculations"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        # Should have changes calculated for forecast years
        assert len(ic.change_in_ar) == forecast_config.n_forecast_years
        assert len(ic.change_in_inventory) == forecast_config.n_forecast_years
        assert len(ic.change_in_ap) == forecast_config.n_forecast_years
    
    def test_min_cash_calculation(self, minimal_inputs, forecast_config):
        """Test minimum cash requirement calculation"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        min_cash_pct = minimal_inputs['min_cash_pct_revenue']  # 0.10
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            expected_min_cash = ic.revenue[year] * min_cash_pct
            assert ic.min_cash_required[year] == pytest.approx(expected_min_cash, rel=1e-6)
    
    def test_goodwill_constant(self, minimal_inputs, forecast_config):
        """Test goodwill remains constant"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        goodwill_0 = minimal_inputs['goodwill_year_0']
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            assert ic.goodwill[year] == goodwill_0
    
    def test_intangible_assets_constant(self, minimal_inputs, forecast_config):
        """Test intangible assets remain constant"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        ic.calculate_all()
        
        intangibles_0 = minimal_inputs['intangible_assets_year_0']
        
        for year in range(1, forecast_config.n_forecast_years + 1):
            assert ic.intangible_assets[year] == intangibles_0
    
    def test_interest_rates_arrays(self, minimal_inputs, forecast_config):
        """Test interest rate arrays are properly set"""
        ic = IntermediateCalculations(minimal_inputs, forecast_config)
        
        # Should have n_forecast_years elements
        assert len(ic.cost_of_debt) == forecast_config.n_forecast_years
        assert len(ic.return_st_investment) == forecast_config.n_forecast_years
        
        # All should be the same value (constant assumption)
        assert all(r == minimal_inputs['cost_of_debt'] for r in ic.cost_of_debt)
        assert all(r == minimal_inputs['return_st_investment'] for r in ic.return_st_investment)
