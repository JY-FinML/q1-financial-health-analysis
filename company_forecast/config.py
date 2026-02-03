"""
Configuration module for company financial forecasting.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ForecastConfig:
    """Configuration for the forecast model"""
    
    # Number of years to forecast
    n_forecast_years: int = 4
    
    # Number of historical years to use as input (for calculating averages/trends)
    n_input_years: int = 3
    
    # Year labels (will be set based on base year)
    base_year: int = 2025
    
    @property
    def forecast_years(self) -> List[int]:
        """Return list of forecast year numbers"""
        return list(range(1, self.n_forecast_years + 1))
    
    @property
    def all_years(self) -> List[int]:
        """Return list of all years including Year 0"""
        return list(range(self.n_forecast_years + 1))
    
    @property
    def year_labels(self) -> List[str]:
        """Return year labels (e.g., 2025, 2026, 2027, ...)"""
        return [str(self.base_year + i) for i in range(self.n_forecast_years + 1)]


@dataclass
class ModelAssumptions:
    """
    Default model assumptions that can be customized per company.
    These are used when historical data is insufficient.
    """
    # Depreciation
    default_depreciation_years: float = 10.0
    
    # Tax rate (will try to calculate from historical data)
    default_tax_rate: float = 0.21
    
    # Debt parameters
    st_loan_years: float = 1.0  # Short-term loans are 1 year
    lt_loan_years: float = 10.0  # Long-term loans are 10 years
    
    # Financing mix (70% debt, 30% equity for new financing needs)
    pct_financing_with_debt: float = 0.70
    
    # Interest rates (real)
    real_interest_rate: float = 0.02
    risk_premium_debt: float = 0.04
    risk_premium_st_investment: float = -0.01
    
    # Payout ratio (dividends / net income)
    default_payout_ratio: float = 0.50
    
    # Working capital ratios (as % of revenue)
    default_ar_pct: float = 0.08  # Accounts receivable
    default_inventory_pct: float = 0.05  # Inventory
    default_ap_pct: float = 0.10  # Accounts payable
    
    # Cash requirements (as % of revenue)
    min_cash_pct_revenue: float = 0.04
    
    # Growth assumptions (if not calculated from historical)
    default_revenue_growth: float = 0.03
    default_inflation_rate: float = 0.025
