"""
Unit tests for DataLoader module.
Tests loading and parsing of historical financial data from CSV files.
"""

import pytest
import pandas as pd
from company_forecast.data_loader import DataLoader


class TestDataLoader:
    """Tests for DataLoader class"""
    
    def test_initialization(self, create_test_company):
        """Test DataLoader initialization"""
        company_folder = create_test_company("TestCo")
        dl = DataLoader(company_folder)
        
        assert dl.company_folder == company_folder
        assert dl.company_name == "TestCo"
        assert dl.income_statement_df is None  # Not loaded yet
        assert dl.balance_sheet_df is None
        assert dl.cash_flow_df is None
    
    def test_load_all_success(self, create_test_company):
        """Test successful loading of all financial statements"""
        company_folder = create_test_company("SampleCo")
        dl = DataLoader(company_folder)
        
        result = dl.load_all()
        
        assert result is True
        assert dl.income_statement_df is not None
        assert dl.balance_sheet_df is not None
        assert dl.cash_flow_df is not None
        assert isinstance(dl.income_statement_df, pd.DataFrame)
        assert isinstance(dl.balance_sheet_df, pd.DataFrame)
        assert isinstance(dl.cash_flow_df, pd.DataFrame)
    
    def test_load_all_sets_years(self, create_test_company):
        """Test that load_all correctly extracts years from data"""
        company_folder = create_test_company("YearTestCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        assert len(dl.years) > 0
        assert dl.latest_year is not None
        assert dl.latest_year == '2023'  # From sample_financial_data
        assert dl.years == ['2023', '2022', '2021']  # Sorted descending
    
    def test_load_all_processes_data(self, create_test_company):
        """Test that load_all processes data into dictionaries"""
        company_folder = create_test_company("ProcessCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        assert isinstance(dl.income_statement, dict)
        assert isinstance(dl.balance_sheet, dict)
        assert isinstance(dl.cash_flow, dict)
        assert len(dl.income_statement) > 0
    
    def test_get_value_basic(self, create_test_company):
        """Test get_value retrieves correct values"""
        company_folder = create_test_company("GetValueCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        # Get latest year value
        revenue = dl.get_value('income', 'Total Revenue')
        assert revenue == 120.0  # From sample_financial_data
        
        # Get specific year value
        revenue_2022 = dl.get_value('income', 'Total Revenue', '2022')
        assert revenue_2022 == 110.0
    
    def test_get_value_balance_sheet(self, create_test_company):
        """Test get_value works for balance sheet"""
        company_folder = create_test_company("BalanceCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        total_assets = dl.get_value('balance', 'Total Assets')
        assert total_assets == 300.0
        
        cash = dl.get_value('balance', 'Cash And Cash Equivalents')
        assert cash == 15.0
    
    def test_get_value_cash_flow(self, create_test_company):
        """Test get_value works for cash flow"""
        company_folder = create_test_company("CashCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        ocf = dl.get_value('cash', 'Operating Cash Flow')
        assert ocf == 30.0
        
        capex = dl.get_value('cash', 'Capital Expenditure')
        assert capex == -15.0
    
    def test_get_value_missing_item(self, create_test_company):
        """Test get_value returns None for missing items"""
        company_folder = create_test_company("MissingCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        value = dl.get_value('income', 'NonexistentItem')
        assert value is None
    
    def test_get_historical_values(self, create_test_company):
        """Test get_historical_values returns dict of all years"""
        company_folder = create_test_company("HistCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        hist = dl.get_historical_values('income', 'Total Revenue')
        
        assert isinstance(hist, dict)
        assert '2023' in hist
        assert '2022' in hist
        assert '2021' in hist
        assert hist['2023'] == 120.0
        assert hist['2022'] == 110.0
    
    def test_calculate_growth_rate_basic(self, create_test_company):
        """Test growth rate calculation"""
        company_folder = create_test_company("GrowthCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        # Revenue growth from 100 to 110 to 120
        # CAGR = (120/100)^(1/2) - 1 ≈ 0.0954
        growth = dl.calculate_growth_rate('income', 'Total Revenue', n_years=2)
        
        assert growth is not None
        assert 0.09 < growth < 0.11  # Approximate check
    
    def test_calculate_growth_rate_single_year(self, create_test_company):
        """Test growth rate with n_years=1"""
        company_folder = create_test_company("Growth1Co")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        # From 2022 (110) to 2023 (120): growth = (120-110)/110 ≈ 0.0909
        growth = dl.calculate_growth_rate('income', 'Total Revenue', n_years=1)
        
        assert growth is not None
        assert 0.08 < growth < 0.10
    
    def test_set_base_year_valid(self, create_test_company):
        """Test set_base_year with valid year"""
        company_folder = create_test_company("BaseCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        # Should have years ['2023', '2022', '2021']
        dl.set_base_year('2022')
        
        assert dl.latest_year == '2022'
        assert dl.years == ['2022', '2021']  # Only 2022 and earlier
        assert '2023' not in dl.years  # 2023 should be excluded
    
    def test_set_base_year_invalid(self, create_test_company):
        """Test set_base_year with invalid year raises error"""
        company_folder = create_test_company("BaseErrCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        with pytest.raises(ValueError, match="not available"):
            dl.set_base_year('2030')  # Future year not in data
    
    def test_set_base_year_filters_data(self, create_test_company):
        """Test that set_base_year affects data retrieval"""
        company_folder = create_test_company("FilterCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        # Before setting base year
        revenue_2023 = dl.get_value('income', 'Total Revenue', '2023')
        assert revenue_2023 == 120.0
        
        # Set base year to 2021
        dl.set_base_year('2021')
        
        # Now 2023 and 2022 should not be accessible as latest
        # latest_year is now 2021
        assert dl.latest_year == '2021'
    
    def test_calculate_average_basic(self, create_test_company):
        """Test calculate_average method"""
        company_folder = create_test_company("AvgCo")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        # Average of [120, 110, 100] = 110
        avg = dl.calculate_average('income', 'Total Revenue', n_years=3)
        
        assert avg is not None
        assert avg == pytest.approx(110.0)
    
    def test_calculate_average_two_years(self, create_test_company):
        """Test calculate_average with n_years=2"""
        company_folder = create_test_company("Avg2Co")
        dl = DataLoader(company_folder)
        dl.load_all()
        
        # Average of [120, 110] = 115
        avg = dl.calculate_average('income', 'Total Revenue', n_years=2)
        
        assert avg == pytest.approx(115.0)
    
    def test_load_missing_file_fails(self, tmp_path):
        """Test that loading from non-existent folder fails gracefully"""
        non_existent = tmp_path / "DoesNotExist"
        dl = DataLoader(str(non_existent))
        
        result = dl.load_all()
        
        assert result is False
