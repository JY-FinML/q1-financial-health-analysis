"""
Generic Company Input Parameter Mapping
Maps company historical data to Year 0 and sets forecast parameters
"""
from typing import Dict
from .data_loader import get_value, load_company_data
from .config import get_year_end_dates, get_company_config


class CompanyInputMapper:
    """Maps company actual data to forecast model input format"""
    
    def __init__(self, company_key: str):
        """
        Initialize input mapper
        
        Args:
            company_key: Company key (e.g., 'ProcterGamble', 'Costco')
        """
        self.company_key = company_key
        self.config = get_company_config(company_key)
        self.year_end_dates = get_year_end_dates(company_key)
        
        # Load company data
        all_data = load_company_data(company_key)
        self.bs = all_data['balance_sheet']
        self.is_ = all_data['income_statement']
        self.cf = all_data['cash_flow']
        
        # Use the last base year as Year 0
        self.year_0 = self.config['base_years'][-1]
        self.year_0_date = self.year_end_dates[self.year_0]
    
    def get_initial_balance_sheet(self) -> Dict[str, float]:
        """Get Year 0 balance sheet"""
        year_0 = {}
        date = self.year_0_date
        
        # Assets
        year_0['cash'] = get_value(self.bs, 'Cash And Cash Equivalents', date)
        year_0['accounts_receivable'] = get_value(self.bs, 'Accounts Receivable', date)
        year_0['inventory'] = get_value(self.bs, 'Inventory', date)
        year_0['current_assets'] = get_value(self.bs, 'Current Assets', date)
        
        year_0['gross_ppe'] = get_value(self.bs, 'Gross PPE', date)
        year_0['accumulated_depreciation'] = abs(get_value(self.bs, 'Accumulated Depreciation', date))
        year_0['net_ppe'] = get_value(self.bs, 'Net PPE', date)
        
        year_0['goodwill'] = get_value(self.bs, 'Goodwill', date)
        year_0['other_intangibles'] = get_value(self.bs, 'Other Intangible Assets', date)
        year_0['other_non_current_assets'] = get_value(self.bs, 'Other Non Current Assets', date)
        
        year_0['total_assets'] = get_value(self.bs, 'Total Assets', date)
        
        # Liabilities
        year_0['accounts_payable'] = get_value(self.bs, 'Accounts Payable', date)
        year_0['short_term_debt'] = get_value(self.bs, 'Current Debt', date)
        year_0['current_liabilities'] = get_value(self.bs, 'Current Liabilities', date)
        
        year_0['long_term_debt'] = get_value(self.bs, 'Long Term Debt', date)
        year_0['total_debt'] = get_value(self.bs, 'Total Debt', date)
        year_0['non_current_liabilities'] = get_value(self.bs, 'Total Non Current Liabilities Net Minority Interest', date)
        year_0['total_liabilities'] = get_value(self.bs, 'Total Liabilities Net Minority Interest', date)
        
        # Equity
        year_0['common_stock'] = get_value(self.bs, 'Common Stock', date)
        year_0['retained_earnings'] = get_value(self.bs, 'Retained Earnings', date)
        year_0['additional_paid_in_capital'] = get_value(self.bs, 'Additional Paid In Capital', date)
        year_0['treasury_stock'] = get_value(self.bs, 'Treasury Stock', date)
        year_0['other_equity'] = get_value(self.bs, 'Other Equity Interest', date)
        year_0['stockholders_equity'] = get_value(self.bs, 'Stockholders Equity', date)
        year_0['total_equity'] = get_value(self.bs, 'Total Equity Gross Minority Interest', date)
        
        return year_0
    
    def calculate_growth_rates(self) -> Dict[str, float]:
        """
        Calculate growth rates (adaptive to all base years)
        Calculates growth rates for all adjacent year pairs and averages them
        """
        growth = {}
        base_years = self.config['base_years']
        
        if len(base_years) < 2:
            growth['revenue_growth'] = 0.03
            growth['cogs_growth'] = 0.03
            growth['opex_growth'] = 0.03
            return growth
        
        revenue_growths = []
        cogs_growths = []
        opex_growths = []
        
        for i in range(len(base_years) - 1):
            year_t = base_years[i]
            year_t1 = base_years[i + 1]
            date_t = self.year_end_dates[year_t]
            date_t1 = self.year_end_dates[year_t1]
            
            rev_t = get_value(self.is_, 'Total Revenue', date_t)
            rev_t1 = get_value(self.is_, 'Total Revenue', date_t1)
            if rev_t > 0:
                revenue_growths.append((rev_t1 - rev_t) / rev_t)
            
            cogs_t = get_value(self.is_, 'Cost Of Revenue', date_t)
            cogs_t1 = get_value(self.is_, 'Cost Of Revenue', date_t1)
            if cogs_t > 0:
                cogs_growths.append((cogs_t1 - cogs_t) / cogs_t)
            
            opex_t = get_value(self.is_, 'Operating Expense', date_t)
            opex_t1 = get_value(self.is_, 'Operating Expense', date_t1)
            if opex_t > 0:
                opex_growths.append((opex_t1 - opex_t) / opex_t)
        
        growth['revenue_growth'] = sum(revenue_growths) / len(revenue_growths) if revenue_growths else 0.03
        growth['cogs_growth'] = sum(cogs_growths) / len(cogs_growths) if cogs_growths else 0.03
        growth['opex_growth'] = sum(opex_growths) / len(opex_growths) if opex_growths else 0.03
        
        return growth
    
    def calculate_financial_ratios(self) -> Dict[str, float]:
        """
        Calculate financial ratios (adaptive to all base years)
        Uses the average of all base years
        """
        ratios = {}
        base_years = self.config['base_years']
        
        ar_to_revenue_list = []
        inventory_to_cogs_list = []
        ap_to_cogs_list = []
        depreciation_rate_list = []
        capex_to_revenue_list = []
        tax_rate_list = []
        dividend_payout_list = []
        repurchase_to_ni_list = []
        interest_rate_list = []
        
        for year in base_years:
            date = self.year_end_dates[year]
            
            revenue = get_value(self.is_, 'Total Revenue', date)
            cogs = get_value(self.is_, 'Cost Of Revenue', date)
            net_income = get_value(self.is_, 'Net Income', date)
            
            ar = get_value(self.bs, 'Accounts Receivable', date)
            if revenue > 0:
                ar_to_revenue_list.append(ar / revenue)
            
            inventory = get_value(self.bs, 'Inventory', date)
            if cogs > 0:
                inventory_to_cogs_list.append(inventory / cogs)
            
            ap = get_value(self.bs, 'Accounts Payable', date)
            if cogs > 0:
                ap_to_cogs_list.append(ap / cogs)
            
            depreciation = get_value(self.is_, 'Reconciled Depreciation', date)
            gross_ppe = get_value(self.bs, 'Gross PPE', date)
            if gross_ppe > 0:
                depreciation_rate_list.append(depreciation / gross_ppe)
            
            capex = abs(get_value(self.cf, 'Capital Expenditure', date))
            if revenue > 0:
                capex_to_revenue_list.append(capex / revenue)
            
            pretax = get_value(self.is_, 'Pretax Income', date)
            tax = get_value(self.is_, 'Tax Provision', date)
            if pretax > 0:
                tax_rate_list.append(tax / pretax)
            
            dividends = abs(get_value(self.cf, 'Cash Dividends Paid', date))
            if net_income > 0:
                dividend_payout_list.append(dividends / net_income)
            
            repurchase = abs(get_value(self.cf, 'Repurchase Of Capital Stock', date))
            if net_income > 0:
                repurchase_to_ni_list.append(repurchase / net_income)
            
            interest_expense = get_value(self.is_, 'Interest Expense', date)
            total_debt = get_value(self.bs, 'Total Debt', date)
            if total_debt > 0:
                interest_rate_list.append(interest_expense / total_debt)
        
        ratios['ar_to_revenue'] = sum(ar_to_revenue_list) / len(ar_to_revenue_list) if ar_to_revenue_list else 0.05
        ratios['inventory_to_cogs'] = sum(inventory_to_cogs_list) / len(inventory_to_cogs_list) if inventory_to_cogs_list else 0.1
        ratios['ap_to_cogs'] = sum(ap_to_cogs_list) / len(ap_to_cogs_list) if ap_to_cogs_list else 0.1
        ratios['depreciation_rate'] = sum(depreciation_rate_list) / len(depreciation_rate_list) if depreciation_rate_list else 0.05
        ratios['capex_to_revenue'] = sum(capex_to_revenue_list) / len(capex_to_revenue_list) if capex_to_revenue_list else 0.04
        ratios['tax_rate'] = sum(tax_rate_list) / len(tax_rate_list) if tax_rate_list else 0.21
        ratios['dividend_payout'] = sum(dividend_payout_list) / len(dividend_payout_list) if dividend_payout_list else 0.6
        ratios['repurchase_to_ni'] = sum(repurchase_to_ni_list) / len(repurchase_to_ni_list) if repurchase_to_ni_list else 0.3
        ratios['interest_rate'] = sum(interest_rate_list) / len(interest_rate_list) if interest_rate_list else 0.03
        
        return ratios
    
    def get_forecast_inputs(self) -> Dict:
        """Generate forecast input parameters"""
        inputs = {}
        
        inputs['base_year'] = self.year_0
        inputs['forecast_years'] = len(self.config['forecast_years'])
        
        inputs['year_0_balance_sheet'] = self.get_initial_balance_sheet()
        
        growth = self.calculate_growth_rates()
        inputs['nominal_revenue_growth'] = [growth['revenue_growth']] * inputs['forecast_years']
        inputs['nominal_cogs_growth'] = [growth['cogs_growth']] * inputs['forecast_years']
        inputs['nominal_opex_growth'] = [growth['opex_growth']] * inputs['forecast_years']
        
        ratios = self.calculate_financial_ratios()
        inputs['ar_days'] = ratios['ar_to_revenue'] * 365
        inputs['inventory_days'] = ratios['inventory_to_cogs'] * 365
        inputs['ap_days'] = ratios['ap_to_cogs'] * 365
        inputs['depreciation_rate'] = ratios['depreciation_rate']
        inputs['capex_to_revenue'] = ratios['capex_to_revenue']
        inputs['tax_rate'] = ratios['tax_rate']
        inputs['dividend_payout_ratio'] = ratios['dividend_payout']
        inputs['repurchase_to_ni_ratio'] = ratios['repurchase_to_ni']
        inputs['interest_rate_st'] = ratios['interest_rate']
        inputs['interest_rate_lt'] = ratios['interest_rate']
        
        cash_list = []
        for year in self.config['base_years']:
            date = self.year_end_dates[year]
            cash = get_value(self.bs, 'Cash And Cash Equivalents', date)
            if cash > 0:
                cash_list.append(cash)
        inputs['min_cash_balance'] = sum(cash_list) / len(cash_list) if cash_list else 5000
        
        debt_to_equity_list = []
        for year in self.config['base_years']:
            date = self.year_end_dates[year]
            total_debt = get_value(self.bs, 'Total Debt', date)
            equity = get_value(self.bs, 'Stockholders Equity', date)
            if equity > 0 and total_debt > 0:
                debt_to_equity_list.append(total_debt / equity)
        inputs['max_debt_to_equity'] = sum(debt_to_equity_list) / len(debt_to_equity_list) if debt_to_equity_list else 0.7
        
        debt_structure_list = []
        for year in self.config['base_years']:
            date = self.year_end_dates[year]
            lt_debt = get_value(self.bs, 'Long Term Debt', date)
            total_debt = get_value(self.bs, 'Total Debt', date)
            if total_debt > 0:
                debt_structure_list.append(lt_debt / total_debt)
        inputs['target_debt_structure'] = sum(debt_structure_list) / len(debt_structure_list) if debt_structure_list else 0.7
        
        inputs['shares_outstanding'] = get_value(self.bs, 'Ordinary Shares Number', self.year_0_date)
        inputs['company_name'] = self.config['name']
        inputs['company_ticker'] = self.config['ticker']
        
        inputs['year_0_revenue'] = get_value(self.is_, 'Total Revenue', self.year_0_date)
        inputs['year_0_cogs'] = get_value(self.is_, 'Cost Of Revenue', self.year_0_date)
        inputs['year_0_opex'] = get_value(self.is_, 'Operating Expense', self.year_0_date)
        inputs['year_0_gross_profit'] = get_value(self.is_, 'Gross Profit', self.year_0_date)
        inputs['year_0_ebit'] = get_value(self.is_, 'EBIT', self.year_0_date)
        inputs['year_0_depreciation'] = get_value(self.is_, 'Reconciled Depreciation', self.year_0_date)
        inputs['year_0_ebitda'] = get_value(self.is_, 'EBITDA', self.year_0_date)
        inputs['year_0_interest_expense'] = get_value(self.is_, 'Interest Expense', self.year_0_date)
        inputs['year_0_interest_income'] = get_value(self.is_, 'Interest Income', self.year_0_date)
        inputs['year_0_pretax_income'] = get_value(self.is_, 'Pretax Income', self.year_0_date)
        inputs['year_0_tax'] = get_value(self.is_, 'Tax Provision', self.year_0_date)
        inputs['year_0_net_income'] = get_value(self.is_, 'Net Income', self.year_0_date)
        
        inputs['year_0_operating_cf'] = get_value(self.cf, 'Operating Cash Flow', self.year_0_date)
        inputs['year_0_capex'] = abs(get_value(self.cf, 'Capital Expenditure', self.year_0_date))
        inputs['year_0_free_cf'] = get_value(self.cf, 'Free Cash Flow', self.year_0_date)
        inputs['year_0_dividends'] = abs(get_value(self.cf, 'Cash Dividends Paid', self.year_0_date))
        
        return inputs
