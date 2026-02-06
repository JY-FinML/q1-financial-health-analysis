"""
Unit tests for CashBudget module.
Tests cash flow calculations including operating, investing, and financing activities.
"""

import pytest
from company_forecast.cash_budget import CashBudget
from company_forecast.debt_schedule import DebtSchedule
from company_forecast.config import ForecastConfig


class IntermediateStub:
    """Stub for IntermediateCalculations with all required attributes"""
    def __init__(self):
        # Asset and depreciation
        self.depreciation = [5, 5, 5, 5, 5]  # Year 0-4
        self.capex = [2, 10, 12, 14, 16]  # Year 0-4
        self.net_ppe = [100, 105, 110, 115, 120]
        
        # Working capital items
        self.accounts_receivable = [10, 12, 14, 16, 18]
        self.inventory = [5, 6, 7, 8, 9]
        self.accounts_payable = [8, 9, 10, 11, 12]
        
        # Working capital changes (Year 1-4 forecasts)
        self.change_in_working_capital = [3, 3, 3, 3]  # ΔAR + ΔInv - ΔAP
        
        # Cash and financing parameters (Year 1-4)
        self.min_cash_required = [50, 55, 60, 65, 70]  # Year 0-4
        self.cost_of_debt = [0.05, 0.05, 0.05, 0.05]  # Year 1-4
        self.return_st_investment = [0.02, 0.02, 0.02, 0.02]  # Year 1-4


class IncomeStatementStub:
    """Stub for IncomeStatement with required attributes"""
    def __init__(self):
        # Net income by year (Year 0-4)
        self.net_income = [20, 22, 24, 26, 28]
        # Dividends declared (Year 0-4)
        self.dividends = [1, 5, 6, 7, 8]


class DebtScheduleStub:
    """Stub for DebtSchedule with get_total_lt_principal_payment method"""
    def __init__(self):
        # Ending balances (Year 0-4)
        self.st_ending_balance = [5, 5, 15, 20, 25]
        self.lt_ending_balance = [20, 15, 10, 5, 0]
    
    def get_total_lt_principal_payment(self, year):
        """Return LT principal payment for the year"""
        # Simplified: return 5 for all years
        return 5.0


class TestCashBudget:
    """Tests for CashBudget class"""
    
    @pytest.fixture
    def cb_inputs(self):
        """Fixture providing inputs for cash budget tests"""
        return {
            # Year 0 historical data
            'operating_cash_flow_year_0': 10,
            'capex_year_0': 2,
            'dividends_paid_year_0': 1,
            'stock_repurchase_year_0': 0,
            'cash_year_0': 50,
            'short_term_debt_year_0': 5,
            'long_term_debt_year_0': 20,
            'accounts_receivable_year_0': 10,
            'inventory_year_0': 5,
            'accounts_payable_year_0': 8,
            # Financing parameters
            'pct_financing_with_debt': 0.7,  # 70% debt, 30% equity
        }
    
    @pytest.fixture
    def config(self):
        """Standard config for testing"""
        return ForecastConfig(n_forecast_years=3)
    
    @pytest.fixture
    def intermediate_stub(self):
        """Return intermediate stub"""
        return IntermediateStub()
    
    def test_initialization(self, cb_inputs, config, intermediate_stub):
        """Test CashBudget initialization"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        
        # Check arrays are initialized as empty (before calculate_year_0)
        assert len(cb.operating_cash_flow) == 0
        assert len(cb.cumulated_ncb) == 0
        assert cb.year_0_calculated == False
    
    def test_calculate_year_0_initialization(self, cb_inputs, config, intermediate_stub):
        """Test Year 0 calculation sets initial balances"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds = DebtSchedule(cb_inputs, config)
        
        st0, lt0, eq0 = cb.calculate_year_0(ds)
        
        # Cumulated NCB should be initialized to cash
        assert cb.cumulated_ncb[0] == cb_inputs['cash_year_0']
        
        # Should return initial debt and equity values
        assert isinstance(st0, (int, float))
        assert isinstance(lt0, (int, float))
        assert isinstance(eq0, (int, float))
    
    def test_calculate_year_basic(self, cb_inputs, config, intermediate_stub):
        """Test basic year calculation"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        # Must call calculate_year_0 first
        cb.calculate_year_0(ds_stub)
        
        # Now calculate year 1 with correct signature
        cb.calculate_year(1, ds_stub, is_stub)
        
        # Arrays should now have 2 elements (Year 0 and Year 1)
        assert len(cb.operating_cash_flow) == 2
        assert len(cb.investing_cash_flow) == 2
        assert len(cb.financing_cash_flow) == 2
    
    def test_operating_cash_flow_calculation(self, cb_inputs, config, intermediate_stub):
        """Test OCF = NI + Depreciation - Change in WC"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        
        # OCF = Net Income + Depreciation - Change in Working Capital
        ni = is_stub.net_income[1]
        depr = intermediate_stub.depreciation[1]
        change_wc = intermediate_stub.change_in_working_capital[0]  # Year 1 uses index 0
        
        expected_ocf = ni + depr - change_wc
        assert cb.operating_cash_flow[1] == pytest.approx(expected_ocf, rel=1e-6)
    
    def test_investing_cash_flow_capex(self, cb_inputs, config, intermediate_stub):
        """Test ICF = -CAPEX"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        
        # ICF = -CAPEX (investment returns are in discretionary CF)
        expected_icf = -intermediate_stub.capex[1]
        assert cb.investing_cash_flow[1] == pytest.approx(expected_icf, rel=1e-6)
    
    def test_financing_cash_flow_components(self, cb_inputs, config, intermediate_stub):
        """Test FCF = new loans - principal payments"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        
        # FCF = ST loan + LT loan - ST principal - LT principal
        expected_fcf = (cb.st_loan[1] + cb.lt_loan[1] - 
                       cb.st_principal_payment[1] - cb.lt_principal_payment[1])
        assert cb.financing_cash_flow[1] == pytest.approx(expected_fcf, rel=1e-4)
    
    def test_owner_transactions(self, cb_inputs, config, intermediate_stub):
        """Test owner transactions (dividends, stock repurchase, equity invested)"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        
        # Owner cash flow = equity invested - dividends - stock repurchase
        expected_owner = (cb.equity_invested[1] - cb.dividends_paid[1] - 
                         cb.stock_repurchase[1])
        assert cb.owner_cash_flow[1] == pytest.approx(expected_owner, rel=1e-6)
    
    def test_discretionary_transactions(self, cb_inputs, config, intermediate_stub):
        """Test discretionary transactions (ST investments)"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        
        # Discretionary CF = redemption + returns - new investment
        expected_disc = (cb.st_investment_redemption[1] + cb.st_investment_return[1] - 
                        cb.st_investment[1])
        assert cb.discretionary_cash_flow[1] == pytest.approx(expected_disc, rel=1e-6)
    
    def test_net_cash_balance_accumulation(self, cb_inputs, config, intermediate_stub):
        """Test ending cash = previous cash + year NCB"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        
        # Cumulated NCB = previous cash + year NCB
        # Year NCB = OCF + ICF + FCF + Owner CF + Discretionary CF
        expected_ncb = cb.cumulated_ncb[0] + cb.year_ncb[1]
        assert cb.cumulated_ncb[1] == pytest.approx(expected_ncb, rel=1e-4)
    
    def test_net_cash_balance_multi_year(self, cb_inputs, config, intermediate_stub):
        """Test NCB accumulation over multiple years"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        cb.calculate_year(2, ds_stub, is_stub)
        
        # Year 2 NCB should build on Year 1
        expected_ncb_2 = cb.cumulated_ncb[1] + cb.year_ncb[2]
        assert cb.cumulated_ncb[2] == pytest.approx(expected_ncb_2, rel=1e-4)
    
    def test_debt_principal_payments(self, cb_inputs, config, intermediate_stub):
        """Test debt principal payments are tracked correctly"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        cb.calculate_year(2, ds_stub, is_stub)
        
        # Principal payments should be positive numbers (representing outflow)
        # ST principal = beginning ST balance (full repayment)
        # LT principal = from debt schedule
        assert cb.st_principal_payment[1] >= 0
        assert cb.lt_principal_payment[1] >= 0
    
    def test_get_summary(self, cb_inputs, config, intermediate_stub):
        """Test get_summary returns complete dictionary"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        
        summary = cb.get_summary()
        
        assert isinstance(summary, dict)
        assert 'Operating Cash Flow' in summary
        assert 'Investing Cash Flow' in summary
        assert 'Financing Cash Flow' in summary
        assert 'Ending Cash' in summary  # Not 'Cumulated NCB'
        assert len(summary['Operating Cash Flow']) == 2
    
    def test_all_arrays_same_length(self, cb_inputs, config, intermediate_stub):
        """Test that all arrays maintain consistent length"""
        cb = CashBudget(cb_inputs, config, intermediate_stub)
        ds_stub = DebtScheduleStub()
        is_stub = IncomeStatementStub()
        
        cb.calculate_year_0(ds_stub)
        cb.calculate_year(1, ds_stub, is_stub)
        cb.calculate_year(2, ds_stub, is_stub)
        
        # All arrays should have length 3 (Year 0, 1, 2)
        expected_len = 3
        assert len(cb.operating_cash_flow) == expected_len
        assert len(cb.investing_cash_flow) == expected_len
        assert len(cb.financing_cash_flow) == expected_len
        assert len(cb.cumulated_ncb) == expected_len
