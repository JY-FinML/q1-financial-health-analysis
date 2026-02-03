"""
Generic Company Financial Forecasting Framework
Supports multiple companies using the same forecasting logic
"""

from .forecaster import CompanyForecaster
from .data_loader import load_company_data
from .input_mapper import CompanyInputMapper

__all__ = ['CompanyForecaster', 'load_company_data', 'CompanyInputMapper']
