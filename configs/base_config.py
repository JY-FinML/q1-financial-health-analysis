"""
Base Configuration Framework for Company-Specific Model Assumptions.

This module defines the structure for company configurations, distinguishing between:
1. FIXED ASSUMPTIONS - Must be provided manually (very few)
2. CALCULATED FROM HISTORY - Derived automatically from financial data

Design Principle: Minimize fixed assumptions to let the model adapt to each company's
actual historical patterns.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
import json


@dataclass
class CompanyConfig:
    """
    Company-specific model configuration.
    
    Parameters are categorized as:
    
    ═══════════════════════════════════════════════════════════════════════════════
    FIXED ASSUMPTIONS (Required - Cannot be derived from data)
    ═══════════════════════════════════════════════════════════════════════════════
    - lt_loan_years: Years to repay long-term debt (company policy/strategy)
    - pct_financing_with_debt: Debt vs equity preference for new financing needs
    
    ═══════════════════════════════════════════════════════════════════════════════
    OPTIONAL OVERRIDES (Calculated from history, but can be overridden if needed)
    ═══════════════════════════════════════════════════════════════════════════════
    - revenue_growth_override: Override calculated revenue growth
    - tax_rate_override: Override calculated effective tax rate
    - payout_ratio_override: Override calculated dividend payout ratio
    - cogs_pct_override: Override calculated COGS % of revenue
    - sga_pct_override: Override calculated SG&A % of revenue
    
    ═══════════════════════════════════════════════════════════════════════════════
    CALCULATED FROM HISTORY (Auto-derived, no input needed)
    ═══════════════════════════════════════════════════════════════════════════════
    - Revenue growth (from historical revenue changes)
    - COGS % of Revenue (historical average)
    - SG&A % of Revenue (historical average)
    - Tax Rate (from Tax Provision / Pretax Income)
    - Payout Ratio (from Dividends / Net Income)
    - Depreciation Years (from Gross PPE / Depreciation)
    - Cost of Debt (from Interest Expense / Total Debt)
    - Working Capital Ratios (AR, Inventory, AP from historical)
    - CapEx % of Revenue (historical average)
    - Return on ST Investments (from Interest Income / Cash)
    """
    
    # ==========================================
    # Company Identification
    # ==========================================
    company_name: str = ""
    company_ticker: str = ""
    description: str = ""
    
    # ==========================================
    # FORECAST SETTINGS (User-defined)
    # ==========================================
    
    # Base year for forecast (Year 0). Set to null/None to use latest available year.
    # For backtest: set to an earlier year (e.g., "2023" to test forecast against 2024-2025 actuals)
    base_year: Optional[str] = None
    
    # Number of years to forecast (default: 2)
    n_forecast_years: int = 2
    
    # Number of historical years to use for calculating ratios (default: 3)
    n_input_years: int = 3
    
    # Is this a backtest run? If True, will compare forecast with actual data
    is_backtest: bool = False
    
    # ==========================================
    # FIXED ASSUMPTIONS (Minimal - Strategy/Policy based)
    # Only 3 fixed assumptions needed!
    # ==========================================
    
    # Long-term debt repayment period (company-specific capital structure strategy)
    # Default: 10 years (typical for corporate bonds)
    lt_loan_years: float = 10.0
    
    # Short-term loan period (typically 1 year by definition)
    st_loan_years: float = 1.0
    
    # Financing mix preference: What % of new financing needs to fund with debt
    # Range: 0.0 (all equity) to 1.0 (all debt)
    # Default: 0.70 (70% debt financing is common for established companies)
    pct_financing_with_debt: float = 0.70
    
    # ==========================================
    # OPTIONAL OVERRIDES (Only set if you want to override calculated values)
    # Leave as None to use values calculated from historical data
    # ==========================================
    
    # Revenue growth override (None = calculate from history)
    revenue_growth_override: Optional[float] = None
    
    # Tax rate override (None = calculate from Tax Provision / Pretax Income)
    tax_rate_override: Optional[float] = None
    
    # Payout ratio override (None = calculate from Dividends / Net Income)
    payout_ratio_override: Optional[float] = None
    
    # COGS % of revenue override (None = calculate from history)
    cogs_pct_override: Optional[float] = None
    
    # SG&A % of revenue override (None = calculate from history)
    sga_pct_override: Optional[float] = None
    
    # CapEx % of revenue override (None = calculate from history)
    capex_pct_override: Optional[float] = None
    
    # Cost of debt override (None = calculate from Interest Expense / Total Debt)
    cost_of_debt_override: Optional[float] = None
    
    # ==========================================
    # BOUNDS AND SAFETY LIMITS
    # ==========================================
    
    # Revenue growth bounds (clip calculated growth to reasonable range)
    min_revenue_growth: float = -0.10
    max_revenue_growth: float = 0.15
    
    # Tax rate bounds
    min_tax_rate: float = 0.10
    max_tax_rate: float = 0.40
    
    # Depreciation years bounds
    min_depreciation_years: float = 5.0
    max_depreciation_years: float = 25.0
    
    # ==========================================
    # DEFAULT VALUES (Used when historical data is missing)
    # ==========================================
    
    # These are only used as fallback when historical data is insufficient
    default_tax_rate: float = 0.21  # US corporate rate
    default_revenue_growth: float = 0.03  # Modest growth
    default_payout_ratio: float = 0.50
    default_ar_pct: float = 0.08
    default_inventory_pct: float = 0.05
    default_ap_pct: float = 0.10
    default_depreciation_years: float = 10.0
    default_inflation_rate: float = 0.025
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'company_name': self.company_name,
            'company_ticker': self.company_ticker,
            'description': self.description,
            # Forecast settings
            'base_year': self.base_year,
            'n_forecast_years': self.n_forecast_years,
            'n_input_years': self.n_input_years,
            'is_backtest': self.is_backtest,
            # Fixed assumptions
            'lt_loan_years': self.lt_loan_years,
            'st_loan_years': self.st_loan_years,
            'pct_financing_with_debt': self.pct_financing_with_debt,
            'real_interest_rate': self.real_interest_rate,
            'risk_premium_st_investment': self.risk_premium_st_investment,
            # Optional overrides
            'revenue_growth_override': self.revenue_growth_override,
            'tax_rate_override': self.tax_rate_override,
            'payout_ratio_override': self.payout_ratio_override,
            'cogs_pct_override': self.cogs_pct_override,
            'sga_pct_override': self.sga_pct_override,
            'capex_pct_override': self.capex_pct_override,
            'cost_of_debt_override': self.cost_of_debt_override,
            # Bounds
            'min_revenue_growth': self.min_revenue_growth,
            'max_revenue_growth': self.max_revenue_growth,
            'min_tax_rate': self.min_tax_rate,
            'max_tax_rate': self.max_tax_rate,
            'min_depreciation_years': self.min_depreciation_years,
            'max_depreciation_years': self.max_depreciation_years,
            # Defaults
            'default_tax_rate': self.default_tax_rate,
            'default_revenue_growth': self.default_revenue_growth,
            'default_payout_ratio': self.default_payout_ratio,
            'default_ar_pct': self.default_ar_pct,
            'default_inventory_pct': self.default_inventory_pct,
            'default_ap_pct': self.default_ap_pct,
            'default_depreciation_years': self.default_depreciation_years,
            'default_inflation_rate': self.default_inflation_rate,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyConfig':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def get_summary(self) -> str:
        """Return formatted summary of configuration"""
        lines = [
            f"\n{'='*70}",
            f"COMPANY CONFIGURATION: {self.company_name} ({self.company_ticker})",
            f"{'='*70}",
            f"\n{self.description}" if self.description else "",
            f"\n{'─'*70}",
            f"FIXED ASSUMPTIONS (Company Strategy/Policy)",
            f"{'─'*70}",
            f"  Long-term Loan Period:      {self.lt_loan_years:.0f} years",
            f"  Short-term Loan Period:     {self.st_loan_years:.0f} year",
            f"  Debt Financing Preference:  {self.pct_financing_with_debt*100:.0f}% debt / {(1-self.pct_financing_with_debt)*100:.0f}% equity",
            f"  Real Interest Rate:         {self.real_interest_rate*100:.1f}%",
            f"\n{'─'*70}",
            f"OPTIONAL OVERRIDES (Only if set - otherwise calculated from history)",
            f"{'─'*70}",
        ]
        
        overrides = {
            'Revenue Growth': self.revenue_growth_override,
            'Tax Rate': self.tax_rate_override,
            'Payout Ratio': self.payout_ratio_override,
            'COGS %': self.cogs_pct_override,
            'SG&A %': self.sga_pct_override,
            'CapEx %': self.capex_pct_override,
            'Cost of Debt': self.cost_of_debt_override,
        }
        
        has_overrides = False
        for name, value in overrides.items():
            if value is not None:
                lines.append(f"  {name}: {value*100:.1f}%")
                has_overrides = True
        
        if not has_overrides:
            lines.append("  (None - all values calculated from historical data)")
        
        lines.extend([
            f"\n{'─'*70}",
            f"AUTO-CALCULATED FROM HISTORY",
            f"{'─'*70}",
            "  ✓ Revenue Growth (from historical revenue changes)",
            "  ✓ COGS % of Revenue (historical average)",
            "  ✓ SG&A % of Revenue (historical average)",
            "  ✓ Tax Rate (Tax Provision / Pretax Income)",
            "  ✓ Payout Ratio (Dividends / Net Income)",
            "  ✓ Depreciation Years (Gross PPE / Depreciation)",
            "  ✓ Cost of Debt (Interest Expense / Total Debt)",
            "  ✓ Working Capital Ratios (AR, Inventory, AP)",
            "  ✓ CapEx % of Revenue",
            f"{'='*70}",
        ])
        return '\n'.join(lines)


def load_company_config(company_name: str, config_dir: str = None) -> CompanyConfig:
    """
    Load company configuration from JSON file.
    
    Args:
        company_name: Name of the company (e.g., 'ProcterGamble')
        config_dir: Directory containing config files (default: ./configs)
    
    Returns:
        CompanyConfig object
    """
    if config_dir is None:
        config_dir = os.path.dirname(__file__)
    
    config_file = os.path.join(config_dir, f"{company_name}.json")
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            data = json.load(f)
        return CompanyConfig.from_dict(data)
    else:
        # Return default config if no company-specific config exists
        print(f"  Note: No specific config found for {company_name}, using defaults")
        return CompanyConfig(company_name=company_name)


def list_available_companies(config_dir: str = None) -> list:
    """List all companies with configuration files"""
    if config_dir is None:
        config_dir = os.path.dirname(__file__)
    
    companies = []
    if os.path.exists(config_dir):
        for f in os.listdir(config_dir):
            if f.endswith('.json'):
                companies.append(f.replace('.json', ''))
    return sorted(companies)
