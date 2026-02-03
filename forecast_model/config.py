"""
Configuration module for financial forecasting model.
Defines the structure and time periods for the forecast.
"""


class ForecastConfig:
    """Configuration class for forecast parameters"""
    
    def __init__(self, n_years=4):
        """
        Initialize forecast configuration
        
        Args:
            n_years: Number of years to forecast (default 4)
        """
        self.n_years = n_years
        self.years = list(range(n_years + 1))  # [0, 1, 2, 3, 4]
        
    def __repr__(self):
        return f"ForecastConfig(n_years={self.n_years})"
