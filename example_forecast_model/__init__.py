"""
Financial Forecasting Model Package

A modular implementation of a comprehensive financial forecasting model
including cash budget, income statement, and balance sheet projections.
"""

from .config import ForecastConfig
from .inputs import InputData
from .intermediate import IntermediateCalculations
from .cash_budget import CashBudget
from .debt_schedule import DebtSchedule
from .income_statement import IncomeStatement
from .balance_sheet import BalanceSheet
from .forecaster import Forecaster

__all__ = [
    'ForecastConfig',
    'InputData',
    'IntermediateCalculations',
    'CashBudget',
    'DebtSchedule',
    'IncomeStatement',
    'BalanceSheet',
    'Forecaster'
]

__version__ = '1.0.0'
