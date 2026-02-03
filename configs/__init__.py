"""
Company-specific configuration files for financial forecasting.

Each company has its own config file with model assumptions.
Only parameters that cannot be reliably derived from historical data
are specified as fixed inputs. Everything else is calculated automatically.
"""

from .base_config import CompanyConfig, load_company_config, list_available_companies

__all__ = ['CompanyConfig', 'load_company_config', 'list_available_companies']
