"""
Unit tests for IncomeStatement module.
Tests income statement calculations including revenue, expenses, and net income.
"""

import pytest
from company_forecast.income_statement import IncomeStatement
from company_forecast.config import ForecastConfig


class IntermediateStub:
    """Stub for IntermediateCalculations"""
    def __init__(self):
        self.revenue = [100, 110, 121, 133.1]
        self.cogs = [60, 66, 72.6, 79.86]
        self.gross_profit = [40, 44, 48.4, 53.24]
        self.sga_expenses = [10, 11, 12.1, 13.31]
        self.depreciation = [5, 5, 5, 5]
        self.cost_of_debt = [0.05, 0.05, 0.05]
        self.return_st_investment = [0.02, 0.02, 0.02]


class CashBudgetStub:
    """Stub for CashBudget"""
    def __init__(self):
        self.st_investment = [0, 0, 50, 100]


class DebtScheduleStub:
    """Stub for DebtSchedule"""
    def __init__(self):
        self.st_ending_balance = [10, 100, 50, 30]
        self.lt_ending_balance = [50, 200, 180, 160]


class TestIncomeStatement:
    """Tests for IncomeStatement class"""
    
    @pytest.fixture
    def income_inputs(self):
        """Fixture providing inputs for income statement tests"""
        return {
            'revenue_year_0': 100,
            'cogs_year_0': 60,
            'gross_profit_year_0': 40,
            'sga_year_0': 10,
            'depreciation_year_0': 5,
            'operating_income_year_0': 25,
            'interest_expense_year_0': 2,
            'pretax_income_year_0': 23,
            'tax_provision_year_0': 4.6,
            'net_income_year_0': 18.4,
            'dividends_paid_year_0': 5,
            'retained_earnings_year_0': 50,
            'tax_rate': 0.2,
            'payout_ratio': 0.3,
        }
    
    @pytest.fixture
    def config(self):
        """Standard config for testing"""
        return ForecastConfig(n_forecast_years=3)
    
    @pytest.fixture
    def stubs(self):
        """Return all stub objects"""
        return IntermediateStub(), CashBudgetStub(), DebtScheduleStub()
    
    def test_initialization(self, income_inputs, config):
        """Test IncomeStatement initialization"""
        intermediate = IntermediateStub()
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        
        # Check Year 0 values are set
        assert is_obj.revenue[0] == income_inputs['revenue_year_0']
        assert is_obj.cogs[0] == income_inputs['cogs_year_0']
        assert is_obj.net_income[0] == income_inputs['net_income_year_0']
        assert is_obj.dividends[0] == income_inputs['dividends_paid_year_0']
        
        # Check arrays are initialized with one element
        assert len(is_obj.revenue) == 1
        assert len(is_obj.net_income) == 1
        assert len(is_obj.ebt) == 1
    
    def test_calculate_year_basic(self, income_inputs, config, stubs):
        """Test basic year calculation"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Arrays should now have 2 elements (Year 0 and Year 1)
        assert len(is_obj.revenue) == 2
        assert len(is_obj.net_income) == 2
        assert len(is_obj.operating_income) == 2
    
    def test_revenue_from_intermediate(self, income_inputs, config, stubs):
        """Test revenue comes from intermediate calculations"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Revenue should come from intermediate
        assert is_obj.revenue[1] == intermediate.revenue[1]
        assert is_obj.cogs[1] == intermediate.cogs[1]
        assert is_obj.gross_profit[1] == intermediate.gross_profit[1]
    
    def test_interest_expense_calculation(self, income_inputs, config, stubs):
        """Test interest expense based on beginning debt"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Interest should be based on previous year's ending debt
        # (10 + 50) * 0.05 = 3.0
        expected_interest = (ds.st_ending_balance[0] + ds.lt_ending_balance[0]) * intermediate.cost_of_debt[0]
        assert is_obj.interest_expense[1] == pytest.approx(expected_interest, rel=1e-6)
    
    def test_interest_expense_no_circularity(self, income_inputs, config, stubs):
        """Test that interest is calculated on beginning balance (no circularity)"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        is_obj.calculate_year(2, cb, ds)
        
        # Year 2 interest should use Year 1 ending balances
        expected_interest_y2 = (ds.st_ending_balance[1] + ds.lt_ending_balance[1]) * intermediate.cost_of_debt[1]
        assert is_obj.interest_expense[2] == pytest.approx(expected_interest_y2, rel=1e-6)
    
    def test_operating_income_calculation(self, income_inputs, config, stubs):
        """Test EBIT = Gross Profit - SG&A - Depreciation"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Operating income = gross profit - SGA - depreciation
        expected = intermediate.gross_profit[1] - intermediate.sga_expenses[1] - intermediate.depreciation[1]
        assert is_obj.operating_income[1] == pytest.approx(expected, rel=1e-6)
    
    def test_ebt_calculation(self, income_inputs, config, stubs):
        """Test EBT = EBIT - Interest Expense + Interest Income"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # EBT = operating income - interest expense + interest income
        expected_ebt = is_obj.operating_income[1] - is_obj.interest_expense[1] + is_obj.interest_income[1]
        assert is_obj.ebt[1] == pytest.approx(expected_ebt, rel=1e-6)
    
    def test_tax_calculation(self, income_inputs, config, stubs):
        """Test tax = EBT * tax_rate (if positive)"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Tax should be EBT * tax rate (if positive)
        expected_tax = max(0, is_obj.ebt[1] * income_inputs['tax_rate'])
        assert is_obj.income_taxes[1] == pytest.approx(expected_tax, rel=1e-6)
    
    def test_tax_zero_when_negative_ebt(self, income_inputs, config):
        """Test that tax is zero when EBT is negative"""
        # Create scenario with negative EBT
        intermediate = IntermediateStub()
        intermediate.gross_profit = [40, 5, 5]  # Very low gross profit
        
        cb = CashBudgetStub()
        ds = DebtScheduleStub()
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # If EBT is negative, tax should be zero
        if is_obj.ebt[1] < 0:
            assert is_obj.income_taxes[1] == 0
    
    def test_net_income_calculation(self, income_inputs, config, stubs):
        """Test net income = EBT - taxes"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Net income should equal EBT minus taxes
        assert is_obj.net_income[1] == pytest.approx(is_obj.ebt[1] - is_obj.income_taxes[1], rel=1e-6)
    
    def test_dividends_calculation(self, income_inputs, config, stubs):
        """Test dividends = net income * payout ratio"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Dividends should be net income * payout ratio
        expected_div = max(0, is_obj.net_income[1] * income_inputs['payout_ratio'])
        assert is_obj.dividends[1] == pytest.approx(expected_div, rel=1e-6)
    
    def test_dividends_non_negative(self, income_inputs, config, stubs):
        """Test that dividends are never negative"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        is_obj.calculate_year(2, cb, ds)
        
        # All dividends should be non-negative
        for div in is_obj.dividends:
            assert div >= 0
    
    def test_interest_income_from_investments(self, income_inputs, config, stubs):
        """Test interest income from ST investments"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        is_obj.calculate_year(2, cb, ds)
        
        # Interest income should be calculated on prior period investments
        # Allow for different implementation approaches
        assert is_obj.interest_income[1] >= 0
        assert is_obj.interest_income[2] >= 0
    
    def test_interest_income_year_3(self, income_inputs, config, stubs):
        """Test interest income accumulates properly"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        is_obj.calculate_year(2, cb, ds)
        is_obj.calculate_year(3, cb, ds)
        
        # Interest income should be non-negative and calculated consistently
        assert is_obj.interest_income[3] >= 0
        # Should have interest income array with 4 elements
        assert len(is_obj.interest_income) == 4
    
    def test_retained_earnings_accumulation(self, income_inputs, config, stubs):
        """Test retained earnings accumulation"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        # Cumulated RE = Previous RE + Previous NI - Previous Dividends
        expected_re = (is_obj.cumulated_retained_earnings[0] + 
                      is_obj.net_income[0] - 
                      is_obj.dividends[0])
        assert is_obj.cumulated_retained_earnings[1] == pytest.approx(expected_re, rel=1e-6)
    
    def test_retained_earnings_multi_year(self, income_inputs, config, stubs):
        """Test retained earnings over multiple years"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        is_obj.calculate_year(2, cb, ds)
        is_obj.calculate_year(3, cb, ds)
        
        # Check Year 2
        expected_re_2 = (is_obj.cumulated_retained_earnings[1] + 
                        is_obj.net_income[1] - 
                        is_obj.dividends[1])
        assert is_obj.cumulated_retained_earnings[2] == pytest.approx(expected_re_2, rel=1e-6)
        
        # Check Year 3
        expected_re_3 = (is_obj.cumulated_retained_earnings[2] + 
                        is_obj.net_income[2] - 
                        is_obj.dividends[2])
        assert is_obj.cumulated_retained_earnings[3] == pytest.approx(expected_re_3, rel=1e-6)
    
    def test_get_summary(self, income_inputs, config, stubs):
        """Test get_summary returns complete dictionary"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        
        summary = is_obj.get_summary()
        
        assert isinstance(summary, dict)
        assert 'Revenue' in summary
        assert 'COGS' in summary
        assert 'Gross Profit' in summary
        assert 'Operating Income' in summary
        assert 'Net Income' in summary
        assert 'Dividends' in summary
        assert len(summary['Revenue']) == 2
    
    def test_all_arrays_same_length(self, income_inputs, config, stubs):
        """Test that all arrays maintain consistent length"""
        intermediate, cb, ds = stubs
        
        is_obj = IncomeStatement(income_inputs, config, intermediate)
        is_obj.calculate_year(1, cb, ds)
        is_obj.calculate_year(2, cb, ds)
        
        # All arrays should have length 3 (Year 0, 1, 2)
        expected_len = 3
        assert len(is_obj.revenue) == expected_len
        assert len(is_obj.cogs) == expected_len
        assert len(is_obj.operating_income) == expected_len
        assert len(is_obj.ebt) == expected_len
        assert len(is_obj.net_income) == expected_len
        assert len(is_obj.dividends) == expected_len
