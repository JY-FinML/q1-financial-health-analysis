"""
P&G输入参数映射
将P&G 2023年数据映射为Year 0，并设置预测参数
"""
from typing import Dict
from .data_loader import get_value, load_all_data
from .config import YEAR_END_DATES


class PGInputMapper:
    """将P&G真实数据映射到forecast model的输入格式"""
    
    def __init__(self):
        all_data = load_all_data()
        self.bs = all_data['balance_sheet']
        self.is_ = all_data['income_statement']
        self.cf = all_data['cash_flow']
        
        # 使用2023年作为Year 0
        self.year_0_date = YEAR_END_DATES[2023]
        
        # 使用2022-2023计算增长率
        self.year_minus_1_date = YEAR_END_DATES[2022]
    
    def get_initial_balance_sheet(self) -> Dict[str, float]:
        """获取Year 0的资产负债表（2023年实际值）"""
        year_0 = {}
        date = self.year_0_date
        
        # 资产
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
        
        # 负债
        year_0['accounts_payable'] = get_value(self.bs, 'Accounts Payable', date)
        year_0['short_term_debt'] = get_value(self.bs, 'Current Debt', date)
        year_0['current_liabilities'] = get_value(self.bs, 'Current Liabilities', date)
        
        year_0['long_term_debt'] = get_value(self.bs, 'Long Term Debt', date)
        year_0['total_debt'] = get_value(self.bs, 'Total Debt', date)
        year_0['non_current_liabilities'] = get_value(self.bs, 'Total Non Current Liabilities Net Minority Interest', date)
        year_0['total_liabilities'] = get_value(self.bs, 'Total Liabilities Net Minority Interest', date)
        
        # 权益
        year_0['common_stock'] = get_value(self.bs, 'Common Stock', date)
        year_0['retained_earnings'] = get_value(self.bs, 'Retained Earnings', date)
        year_0['additional_paid_in_capital'] = get_value(self.bs, 'Additional Paid In Capital', date)
        year_0['treasury_stock'] = get_value(self.bs, 'Treasury Stock', date)
        year_0['other_equity'] = get_value(self.bs, 'Other Equity Interest', date)
        year_0['stockholders_equity'] = get_value(self.bs, 'Stockholders Equity', date)
        year_0['total_equity'] = get_value(self.bs, 'Total Equity Gross Minority Interest', date)
        
        return year_0
    
    def calculate_growth_rates(self) -> Dict[str, float]:
        """计算2022-2023的增长率用于预测"""
        growth = {}
        
        # 收入增长率
        rev_2022 = get_value(self.is_, 'Total Revenue', self.year_minus_1_date)
        rev_2023 = get_value(self.is_, 'Total Revenue', self.year_0_date)
        growth['revenue_growth'] = (rev_2023 - rev_2022) / rev_2022 if rev_2022 != 0 else 0
        
        # COGS增长率
        cogs_2022 = get_value(self.is_, 'Cost Of Revenue', self.year_minus_1_date)
        cogs_2023 = get_value(self.is_, 'Cost Of Revenue', self.year_0_date)
        growth['cogs_growth'] = (cogs_2023 - cogs_2022) / cogs_2022 if cogs_2022 != 0 else 0
        
        # 运营费用增长率
        opex_2022 = get_value(self.is_, 'Operating Expense', self.year_minus_1_date)
        opex_2023 = get_value(self.is_, 'Operating Expense', self.year_0_date)
        growth['opex_growth'] = (opex_2023 - opex_2022) / opex_2022 if opex_2022 != 0 else 0
        
        return growth
    
    def calculate_financial_ratios(self) -> Dict[str, float]:
        """计算财务比率"""
        ratios = {}
        date = self.year_0_date
        
        revenue = get_value(self.is_, 'Total Revenue', date)
        
        # 应收账款/收入
        ar = get_value(self.bs, 'Accounts Receivable', date)
        ratios['ar_to_revenue'] = ar / revenue if revenue != 0 else 0.05
        
        # 存货/COGS
        inventory = get_value(self.bs, 'Inventory', date)
        cogs = get_value(self.is_, 'Cost Of Revenue', date)
        ratios['inventory_to_cogs'] = inventory / cogs if cogs != 0 else 0.1
        
        # 应付账款/COGS
        ap = get_value(self.bs, 'Accounts Payable', date)
        ratios['ap_to_cogs'] = ap / cogs if cogs != 0 else 0.1
        
        # 折旧率
        depreciation = get_value(self.is_, 'Reconciled Depreciation', date)
        gross_ppe = get_value(self.bs, 'Gross PPE', date)
        ratios['depreciation_rate'] = depreciation / gross_ppe if gross_ppe != 0 else 0.05
        
        # 资本支出/收入
        capex = abs(get_value(self.cf, 'Capital Expenditure', date))
        ratios['capex_to_revenue'] = capex / revenue if revenue != 0 else 0.04
        
        # 有效税率
        pretax = get_value(self.is_, 'Pretax Income', date)
        tax = get_value(self.is_, 'Tax Provision', date)
        ratios['tax_rate'] = tax / pretax if pretax != 0 else 0.21
        
        # 股息支付率
        net_income = get_value(self.is_, 'Net Income', date)
        dividends = abs(get_value(self.cf, 'Cash Dividends Paid', date))
        ratios['dividend_payout'] = dividends / net_income if net_income != 0 else 0.6
        
        # 利息率（基于债务）
        interest_expense = get_value(self.is_, 'Interest Expense', date)
        total_debt = get_value(self.bs, 'Total Debt', date)
        ratios['interest_rate'] = interest_expense / total_debt if total_debt != 0 else 0.03
        
        return ratios
    
    def get_forecast_inputs(self) -> Dict:
        """
        生成类似原始forecast model的inputs
        但基于P&G真实数据
        """
        inputs = {}
        
        # 基础年份（Year 0 = 2023）
        inputs['base_year'] = 2023
        inputs['forecast_years'] = 2  # 预测2024-2025
        
        # Year 0资产负债表
        inputs['year_0_balance_sheet'] = self.get_initial_balance_sheet()
        
        # 增长率
        growth = self.calculate_growth_rates()
        inputs['nominal_revenue_growth'] = [growth['revenue_growth']] * 2  # 假设保持稳定
        inputs['nominal_cogs_growth'] = [growth['cogs_growth']] * 2
        inputs['nominal_opex_growth'] = [growth['opex_growth']] * 2
        
        # 财务比率
        ratios = self.calculate_financial_ratios()
        inputs['ar_days'] = ratios['ar_to_revenue'] * 365
        inputs['inventory_days'] = ratios['inventory_to_cogs'] * 365
        inputs['ap_days'] = ratios['ap_to_cogs'] * 365
        inputs['depreciation_rate'] = ratios['depreciation_rate']
        inputs['capex_to_revenue'] = ratios['capex_to_revenue']
        inputs['tax_rate'] = ratios['tax_rate']
        inputs['dividend_payout_ratio'] = ratios['dividend_payout']
        inputs['interest_rate_st'] = ratios['interest_rate']
        inputs['interest_rate_lt'] = ratios['interest_rate']
        
        # 最低现金要求（基于2022-2023年历史平均）
        cash_2022 = get_value(self.bs, 'Cash And Cash Equivalents', YEAR_END_DATES[2022])
        cash_2023 = get_value(self.bs, 'Cash And Cash Equivalents', YEAR_END_DATES[2023])
        inputs['min_cash_balance'] = (cash_2022 + cash_2023) / 2
        
        # 债务政策（基于2022-2023年历史平均）
        total_debt_2022 = get_value(self.bs, 'Total Debt', YEAR_END_DATES[2022])
        total_debt_2023 = get_value(self.bs, 'Total Debt', YEAR_END_DATES[2023])
        equity_2022 = get_value(self.bs, 'Stockholders Equity', YEAR_END_DATES[2022])
        equity_2023 = get_value(self.bs, 'Stockholders Equity', YEAR_END_DATES[2023])
        inputs['max_debt_to_equity'] = ((total_debt_2022/equity_2022) + (total_debt_2023/equity_2023)) / 2
        
        # 债务结构（长期债务占比）
        lt_debt_2022 = get_value(self.bs, 'Long Term Debt', YEAR_END_DATES[2022])
        lt_debt_2023 = get_value(self.bs, 'Long Term Debt', YEAR_END_DATES[2023])
        inputs['target_debt_structure'] = ((lt_debt_2022/total_debt_2022) + (lt_debt_2023/total_debt_2023)) / 2
        
        # 股票回购（基于2022-2023年历史平均）
        repurchase_2022 = abs(get_value(self.cf, 'Repurchase Of Capital Stock', YEAR_END_DATES[2022]))
        repurchase_2023 = abs(get_value(self.cf, 'Repurchase Of Capital Stock', YEAR_END_DATES[2023]))
        inputs['stock_repurchase'] = (repurchase_2022 + repurchase_2023) / 2
        
        # 其他参数
        inputs['shares_outstanding'] = get_value(self.bs, 'Ordinary Shares Number', self.year_0_date)
        
        # 2023年实际利润表数据（Year 0）
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
        
        # 2023年现金流数据（Year 0）
        inputs['year_0_operating_cf'] = get_value(self.cf, 'Operating Cash Flow', self.year_0_date)
        inputs['year_0_capex'] = abs(get_value(self.cf, 'Capital Expenditure', self.year_0_date))
        inputs['year_0_free_cf'] = get_value(self.cf, 'Free Cash Flow', self.year_0_date)
        inputs['year_0_dividends'] = abs(get_value(self.cf, 'Cash Dividends Paid', self.year_0_date))
        
        return inputs
    
    def print_mapping_summary(self):
        """打印映射摘要"""
        print("\n" + "="*80)
        print("P&G数据映射摘要")
        print("="*80)
        
        inputs = self.get_forecast_inputs()
        
        print(f"\n【基础设置】")
        print(f"Year 0 (基准年): 2023")
        print(f"预测年份: 2024-2025 (2年)")
        
        print(f"\n【Year 0 资产负债表】(2023年实际值)")
        bs = inputs['year_0_balance_sheet']
        print(f"总资产: ${bs['total_assets']:,.0f}M")
        print(f"现金: ${bs['cash']:,.0f}M")
        print(f"应收账款: ${bs['accounts_receivable']:,.0f}M")
        print(f"存货: ${bs['inventory']:,.0f}M")
        print(f"总负债: ${bs['total_liabilities']:,.0f}M")
        print(f"股东权益: ${bs['stockholders_equity']:,.0f}M")
        print(f"检查平衡: 资产={bs['total_assets']:,.0f}, 负债+权益={bs['total_liabilities'] + bs['total_equity']:,.0f}")
        
        print(f"\n【预测假设】")
        print(f"收入增长率: {inputs['nominal_revenue_growth'][0]:.2%}")
        print(f"COGS增长率: {inputs['nominal_cogs_growth'][0]:.2%}")
        print(f"运营费用增长率: {inputs['nominal_opex_growth'][0]:.2%}")
        print(f"应收账款天数: {inputs['ar_days']:.1f}")
        print(f"存货天数: {inputs['inventory_days']:.1f}")
        print(f"应付账款天数: {inputs['ap_days']:.1f}")
        print(f"税率: {inputs['tax_rate']:.2%}")
        print(f"股息支付率: {inputs['dividend_payout_ratio']:.2%}")
        
        print("\n" + "="*80)
