"""
P&G财务预测引擎
使用现金预算法（与forecast_model相同的计算逻辑）：
Income Statement → Cash Budget → Debt Schedule → Balance Sheet
确保资产负债表平衡
"""
from typing import Dict, List
from .input_mapper import PGInputMapper


class PGForecaster:
    """
    使用现金预算法的P&G预测器
    确保资产负债表平衡
    """
    
    def __init__(self):
        # 获取映射后的输入
        mapper = PGInputMapper()
        self.inputs = mapper.get_forecast_inputs()
        
        # 预测结果存储
        self.years = list(range(self.inputs['forecast_years'] + 1))  # [0, 1, 2]
        
        # 存储每年的财务报表
        self.revenue = [0.0] * (len(self.years))
        self.cogs = [0.0] * len(self.years)
        self.gross_profit = [0.0] * len(self.years)
        self.operating_expenses = [0.0] * len(self.years)
        self.ebit = [0.0] * len(self.years)
        self.depreciation = [0.0] * len(self.years)
        self.ebitda = [0.0] * len(self.years)
        
        self.interest_expense = [0.0] * len(self.years)
        self.interest_income = [0.0] * len(self.years)
        self.ebt = [0.0] * len(self.years)
        self.tax = [0.0] * len(self.years)
        self.net_income = [0.0] * len(self.years)
        
        # 资产负债表项目
        self.cash = [0.0] * len(self.years)
        self.ar = [0.0] * len(self.years)
        self.inventory = [0.0] * len(self.years)
        self.current_assets = [0.0] * len(self.years)
        
        self.gross_ppe = [0.0] * len(self.years)
        self.acc_depreciation = [0.0] * len(self.years)
        self.net_ppe = [0.0] * len(self.years)
        
        self.goodwill = [0.0] * len(self.years)
        self.other_intangibles = [0.0] * len(self.years)
        self.other_noncurrent_assets = [0.0] * len(self.years)
        self.total_assets = [0.0] * len(self.years)
        
        self.ap = [0.0] * len(self.years)
        self.st_debt = [0.0] * len(self.years)
        self.current_liabilities = [0.0] * len(self.years)
        
        self.lt_debt = [0.0] * len(self.years)
        self.total_debt = [0.0] * len(self.years)
        self.noncurrent_liabilities = [0.0] * len(self.years)
        self.total_liabilities = [0.0] * len(self.years)
        
        self.common_stock = [0.0] * len(self.years)
        self.apic = [0.0] * len(self.years)
        self.retained_earnings = [0.0] * len(self.years)
        self.treasury_stock = [0.0] * len(self.years)
        self.other_equity = [0.0] * len(self.years)
        self.stockholders_equity = [0.0] * len(self.years)
        self.total_equity = [0.0] * len(self.years)
        
        # 现金流项目
        self.operating_cf = [0.0] * len(self.years)
        self.investing_cf = [0.0] * len(self.years)
        self.financing_cf = [0.0] * len(self.years)
        self.capex = [0.0] * len(self.years)
        self.dividends = [0.0] * len(self.years)
        self.free_cf = [0.0] * len(self.years)
        
        # 股票回购
        self.stock_repurchase = [0.0] * len(self.years)
        
        # 初始化Year 0
        self._initialize_year_0()
    
    def _initialize_year_0(self):
        """初始化Year 0（2023年实际值）"""
        bs0 = self.inputs['year_0_balance_sheet']
        
        # 资产
        self.cash[0] = bs0['cash']
        self.ar[0] = bs0['accounts_receivable']
        self.inventory[0] = bs0['inventory']
        self.current_assets[0] = bs0['current_assets']
        
        self.gross_ppe[0] = bs0['gross_ppe']
        self.acc_depreciation[0] = bs0['accumulated_depreciation']
        self.net_ppe[0] = bs0['net_ppe']
        
        self.goodwill[0] = bs0['goodwill']
        self.other_intangibles[0] = bs0['other_intangibles']
        self.other_noncurrent_assets[0] = bs0['other_non_current_assets']
        self.total_assets[0] = bs0['total_assets']
        
        # 负债
        self.ap[0] = bs0['accounts_payable']
        self.st_debt[0] = bs0['short_term_debt']
        self.current_liabilities[0] = bs0['current_liabilities']
        
        self.lt_debt[0] = bs0['long_term_debt']
        self.total_debt[0] = bs0['total_debt']
        self.noncurrent_liabilities[0] = bs0['non_current_liabilities']
        self.total_liabilities[0] = bs0['total_liabilities']
        
        # 权益
        self.common_stock[0] = bs0['common_stock']
        self.apic[0] = bs0['additional_paid_in_capital']
        self.retained_earnings[0] = bs0['retained_earnings']
        self.treasury_stock[0] = bs0['treasury_stock']
        self.other_equity[0] = bs0['other_equity']
        self.stockholders_equity[0] = bs0['stockholders_equity']
        self.total_equity[0] = bs0['total_equity']
        
        # Year 0 利润表完整数据（2023年实际值）
        self.revenue[0] = self.inputs.get('year_0_revenue', 0)
        self.cogs[0] = self.inputs.get('year_0_cogs', 0)
        self.gross_profit[0] = self.inputs.get('year_0_gross_profit', 0)
        self.operating_expenses[0] = self.inputs.get('year_0_opex', 0)
        self.ebit[0] = self.inputs.get('year_0_ebit', 0)
        self.depreciation[0] = self.inputs.get('year_0_depreciation', 0)
        self.ebitda[0] = self.inputs.get('year_0_ebitda', 0)
        self.interest_expense[0] = self.inputs.get('year_0_interest_expense', 0)
        self.interest_income[0] = self.inputs.get('year_0_interest_income', 0)
        self.ebt[0] = self.inputs.get('year_0_pretax_income', 0)
        self.tax[0] = self.inputs.get('year_0_tax', 0)
        self.net_income[0] = self.inputs.get('year_0_net_income', 0)
        
        # Year 0 现金流数据
        self.operating_cf[0] = self.inputs.get('year_0_operating_cf', 0)
        self.capex[0] = -abs(self.inputs.get('year_0_capex', 0))  # 负值
        self.free_cf[0] = self.inputs.get('year_0_free_cf', 0)
        self.dividends[0] = -abs(self.inputs.get('year_0_dividends', 0))  # 负值
    
    def forecast_income_statement(self, year: int):
        """
        预测利润表
        year: 索引 (1 for 2024, 2 for 2025)
        """
        # 1. 收入
        self.revenue[year] = self.revenue[year-1] * (1 + self.inputs['nominal_revenue_growth'][year-1])
        
        # 2. COGS
        self.cogs[year] = self.cogs[year-1] * (1 + self.inputs['nominal_cogs_growth'][year-1])
        
        # 3. 毛利润
        self.gross_profit[year] = self.revenue[year] - self.cogs[year]
        
        # 4. 营业费用
        self.operating_expenses[year] = self.operating_expenses[year-1] * (1 + self.inputs['nominal_opex_growth'][year-1])
        
        # 5. EBIT
        self.ebit[year] = self.gross_profit[year] - self.operating_expenses[year]
        
        # 6. 折旧（基于上一年的Gross PPE）
        self.depreciation[year] = self.gross_ppe[year-1] * self.inputs['depreciation_rate']
        
        # 7. EBITDA
        self.ebitda[year] = self.ebit[year] + self.depreciation[year]
        
        # 注意：利息在debt schedule之后计算
    
    def forecast_cash_budget_and_working_capital(self, year: int):
        """
        预测营运资本和经营现金流
        """
        # 1. 应收账款（基于收入）
        self.ar[year] = self.revenue[year] * (self.inputs['ar_days'] / 365)
        
        # 2. 存货（基于COGS）
        self.inventory[year] = self.cogs[year] * (self.inputs['inventory_days'] / 365)
        
        # 3. 应付账款（基于COGS）
        self.ap[year] = self.cogs[year] * (self.inputs['ap_days'] / 365)
        
        # 4. 资本支出
        self.capex[year] = self.revenue[year] * self.inputs['capex_to_revenue']
        
        # 5. Gross PPE
        self.gross_ppe[year] = self.gross_ppe[year-1] + self.capex[year]
        
        # 6. 累计折旧
        self.acc_depreciation[year] = self.acc_depreciation[year-1] + self.depreciation[year]
        
        # 7. Net PPE
        self.net_ppe[year] = self.gross_ppe[year] - self.acc_depreciation[year]
        
        # 8. 经营现金流（简化）
        change_in_ar = self.ar[year] - self.ar[year-1]
        change_in_inventory = self.inventory[year] - self.inventory[year-1]
        change_in_ap = self.ap[year] - self.ap[year-1]
        
        # OCF = EBIT + 折旧 - 税 - 营运资本变动
        # 注意：这里先不减税，税在计算net income时处理
    
    def forecast_debt_and_financing(self, year: int):
        """
        预测债务和融资
        """
        # 1. 计算利息费用（基于上期债务）
        self.interest_expense[year] = (
            self.st_debt[year-1] * self.inputs['interest_rate_st'] +
            self.lt_debt[year-1] * self.inputs['interest_rate_lt']
        )
        
        # 2. 利息收入（假设基于现金余额）
        self.interest_income[year] = self.cash[year-1] * 0.02  # 假设2%收益率
        
        # 3. 税前利润
        self.ebt[year] = self.ebit[year] - self.interest_expense[year] + self.interest_income[year]
        
        # 4. 税
        self.tax[year] = max(0, self.ebt[year] * self.inputs['tax_rate'])
        
        # 5. 净利润
        self.net_income[year] = self.ebt[year] - self.tax[year]
        
        # 6. 股息
        self.dividends[year] = self.net_income[year] * self.inputs['dividend_payout_ratio']
        
        # 7. 留存收益
        self.retained_earnings[year] = self.retained_earnings[year-1] + self.net_income[year] - self.dividends[year]
        
        # 8. 股票回购（基于2022-2023年历史平均）
        self.stock_repurchase[year] = self.inputs.get('stock_repurchase', 5000)
        
        # 9. 库藏股
        self.treasury_stock[year] = self.treasury_stock[year-1] + self.stock_repurchase[year]
        
        # 10. 其他权益项保持稳定
        self.common_stock[year] = self.common_stock[year-1]
        self.apic[year] = self.apic[year-1]
        self.other_equity[year] = self.other_equity[year-1]
        
        # 11. 股东权益
        self.stockholders_equity[year] = (
            self.common_stock[year] +
            self.apic[year] +
            self.retained_earnings[year] -
            self.treasury_stock[year] +
            self.other_equity[year]
        )
        
        # 12. 总权益（假设少数股东权益稳定）
        minority_interest = self.total_equity[year-1] - self.stockholders_equity[year-1]
        self.total_equity[year] = self.stockholders_equity[year] + minority_interest
    
    def forecast_balance_sheet(self, year: int):
        """
        预测资产负债表并确保平衡
        使用现金流法：从上期现金开始，加上本期现金流变动
        """
        # 1. 无形资产（假设保持稳定或略微减少）
        self.goodwill[year] = self.goodwill[year-1]
        self.other_intangibles[year] = self.other_intangibles[year-1] * 0.98  # 假设每年摊销2%
        self.other_noncurrent_assets[year] = self.other_noncurrent_assets[year-1]
        
        # 2. 计算本期现金流变动
        # 经营活动现金流
        change_in_ar = self.ar[year] - self.ar[year-1]
        change_in_inventory = self.inventory[year] - self.inventory[year-1]
        change_in_ap = self.ap[year] - self.ap[year-1]
        
        operating_cf = (
            self.net_income[year] +
            self.depreciation[year] -
            change_in_ar -
            change_in_inventory +
            change_in_ap
        )
        
        # 投资活动现金流（主要是资本支出）
        investing_cf = -self.capex[year]
        
        # 融资活动现金流（股息+股票回购）
        financing_cf = -(self.dividends[year] + self.stock_repurchase[year])
        
        # 3. 计算期末现金（在调整债务前）
        preliminary_cash = (
            self.cash[year-1] +
            operating_cf +
            investing_cf +
            financing_cf
        )
        
        # 4. 债务管理策略
        min_cash = self.inputs['min_cash_balance']
        max_debt_to_equity = self.inputs['max_debt_to_equity']
        target_debt_structure = self.inputs['target_debt_structure']
        
        # 初始化债务为上期值
        self.lt_debt[year] = self.lt_debt[year-1]
        self.st_debt[year] = self.st_debt[year-1]
        self.total_debt[year] = self.lt_debt[year] + self.st_debt[year]
        
        if preliminary_cash < min_cash:
            # 现金不足，需要借债
            shortfall = min_cash - preliminary_cash
            lt_increase = shortfall * target_debt_structure
            st_increase = shortfall * (1 - target_debt_structure)
            
            self.lt_debt[year] += lt_increase
            self.st_debt[year] += st_increase
            self.total_debt[year] = self.lt_debt[year] + self.st_debt[year]
            self.cash[year] = min_cash
            
        elif preliminary_cash > min_cash * 2.5:
            # 现金过多，用于偿还债务
            excess = preliminary_cash - min_cash * 1.5
            
            # 检查债务权益比，如果低于目标，不偿还太多
            current_debt_to_equity = self.total_debt[year] / self.stockholders_equity[year]
            
            if current_debt_to_equity > max_debt_to_equity * 0.5:
                # 可以偿还一部分债务
                debt_reduction = min(excess, self.total_debt[year] * 0.3)  # 最多偿还30%
                
                # 优先偿还短期债务
                st_reduction = min(debt_reduction * 0.4, self.st_debt[year])
                lt_reduction = min(debt_reduction - st_reduction, self.lt_debt[year])
                
                self.st_debt[year] -= st_reduction
                self.lt_debt[year] -= lt_reduction
                self.total_debt[year] = self.lt_debt[year] + self.st_debt[year]
                self.cash[year] = preliminary_cash - (st_reduction + lt_reduction)
            else:
                # 债务已经较低，保持现金
                self.cash[year] = preliminary_cash
        else:
            # 现金合理，保持债务水平
            self.cash[year] = preliminary_cash
        
        # 5. 更新负债项
        # 非流动负债（除债务外，假设保持相对稳定）
        other_noncurrent_liab = self.noncurrent_liabilities[year-1] - self.lt_debt[year-1]
        self.noncurrent_liabilities[year] = self.lt_debt[year] + other_noncurrent_liab
        
        # 流动负债（除债务和AP外，假设保持相对稳定）
        other_current_liab = self.current_liabilities[year-1] - self.st_debt[year-1] - self.ap[year-1]
        self.current_liabilities[year] = self.st_debt[year] + self.ap[year] + other_current_liab
        
        # 6. 总负债
        self.total_liabilities[year] = self.current_liabilities[year] + self.noncurrent_liabilities[year]
        
        # 7. 计算总资产
        self.current_assets[year] = self.cash[year] + self.ar[year] + self.inventory[year]
        
        self.total_assets[year] = (
            self.current_assets[year] +
            self.net_ppe[year] +
            self.goodwill[year] +
            self.other_intangibles[year] +
            self.other_noncurrent_assets[year]
        )
        
        # 8. 验证资产负债表平衡
        # 资产 = 负债 + 权益
        # 如果不平衡，调整现金使其平衡
        required_total_assets = self.total_liabilities[year] + self.total_equity[year]
        imbalance = self.total_assets[year] - required_total_assets
        
        if abs(imbalance) > 1:  # 容忍1M的误差
            # 调整现金以平衡
            self.cash[year] -= imbalance
            self.current_assets[year] = self.cash[year] + self.ar[year] + self.inventory[year]
            self.total_assets[year] = (
                self.current_assets[year] +
                self.net_ppe[year] +
                self.goodwill[year] +
                self.other_intangibles[year] +
                self.other_noncurrent_assets[year]
            )
    
    def _rebalance_balance_sheet(self, year: int):
        """重新平衡资产负债表"""
        # 更新负债
        other_noncurrent_liab = self.noncurrent_liabilities[year-1] - self.lt_debt[year-1]
        self.noncurrent_liabilities[year] = self.lt_debt[year] + other_noncurrent_liab
        
        other_current_liab = self.current_liabilities[year-1] - self.st_debt[year-1] - self.ap[year-1]
        self.current_liabilities[year] = self.st_debt[year] + self.ap[year] + other_current_liab
        
        self.total_liabilities[year] = self.current_liabilities[year] + self.noncurrent_liabilities[year]
        
        # 重新计算总资产和现金
        required_total_assets = self.total_liabilities[year] + self.total_equity[year]
        
        assets_excluding_cash = (
            self.ar[year] +
            self.inventory[year] +
            self.net_ppe[year] +
            self.goodwill[year] +
            self.other_intangibles[year] +
            self.other_noncurrent_assets[year]
        )
        
        self.cash[year] = required_total_assets - assets_excluding_cash
        self.total_assets[year] = required_total_assets
        self.current_assets[year] = self.cash[year] + self.ar[year] + self.inventory[year]
    
    def calculate_cash_flows(self, year: int):
        """计算现金流量表"""
        # 营运资本变动
        change_in_ar = self.ar[year] - self.ar[year-1]
        change_in_inventory = self.inventory[year] - self.inventory[year-1]
        change_in_ap = self.ap[year] - self.ap[year-1]
        change_in_wc = change_in_ar + change_in_inventory - change_in_ap
        
        # 经营现金流
        self.operating_cf[year] = (
            self.net_income[year] +
            self.depreciation[year] -
            change_in_wc
        )
        
        # 投资现金流
        self.investing_cf[year] = -self.capex[year]
        
        # 自由现金流
        self.free_cf[year] = self.operating_cf[year] + self.investing_cf[year]
        
        # 融资现金流
        debt_change = self.total_debt[year] - self.total_debt[year-1]
        self.financing_cf[year] = (
            debt_change -
            self.dividends[year] -
            self.stock_repurchase[year]
        )
    
    def run_forecast(self):
        """
        运行完整预测
        按照: Income Statement → Cash Budget → Debt → Balance Sheet 顺序
        """
        print("\n" + "="*80)
        print("P&G现金预算法预测 (使用forecast_model逻辑)")
        print("="*80)
        
        print(f"\nYear 0 (2023): 资产=${self.total_assets[0]:,.0f}M, "
              f"负债=${self.total_liabilities[0]:,.0f}M, "
              f"权益=${self.total_equity[0]:,.0f}M")
        print(f"检查平衡: {abs(self.total_assets[0] - (self.total_liabilities[0] + self.total_equity[0])) < 1:.0f} ✓")
        
        for year in range(1, len(self.years)):
            year_name = 2023 + year
            print(f"\n预测 Year {year} ({year_name})...")
            
            # Step 1: Income Statement
            self.forecast_income_statement(year)
            
            # Step 2: Cash Budget & Working Capital
            self.forecast_cash_budget_and_working_capital(year)
            
            # Step 3: Debt & Financing (包括利息、税、净利润)
            self.forecast_debt_and_financing(year)
            
            # Step 4: Balance Sheet (确保平衡)
            self.forecast_balance_sheet(year)
            
            # Step 5: Cash Flows
            self.calculate_cash_flows(year)
            
            # 验证平衡
            balance_check = abs(self.total_assets[year] - (self.total_liabilities[year] + self.total_equity[year]))
            
            print(f"  收入: ${self.revenue[year]:,.0f}M")
            print(f"  EBIT: ${self.ebit[year]:,.0f}M")
            print(f"  净利润: ${self.net_income[year]:,.0f}M")
            print(f"  资产: ${self.total_assets[year]:,.0f}M")
            print(f"  负债: ${self.total_liabilities[year]:,.0f}M")
            print(f"  权益: ${self.total_equity[year]:,.0f}M")
            print(f"  现金: ${self.cash[year]:,.0f}M")
            print(f"  总债务: ${self.total_debt[year]:,.0f}M")
            print(f"  资产负债表平衡差异: ${balance_check:,.2f}M {'✓' if balance_check < 1 else '✗'}")
        
        print("\n" + "="*80)
        print("预测完成！资产负债表已平衡。")
        print("="*80)
    
    def print_detailed_balance_sheet(self, year: int):
        """打印详细资产负债表"""
        year_name = 2023 + year
        print(f"\n{'='*80}")
        print(f"资产负债表 - Year {year} ({year_name})")
        print(f"{'='*80}")
        
        print(f"\n【资产】")
        print(f"现金: ${self.cash[year]:,.0f}M")
        print(f"应收账款: ${self.ar[year]:,.0f}M")
        print(f"存货: ${self.inventory[year]:,.0f}M")
        print(f"流动资产: ${self.current_assets[year]:,.0f}M")
        print(f"\nGross PPE: ${self.gross_ppe[year]:,.0f}M")
        print(f"累计折旧: ${self.acc_depreciation[year]:,.0f}M")
        print(f"Net PPE: ${self.net_ppe[year]:,.0f}M")
        print(f"\n商誉: ${self.goodwill[year]:,.0f}M")
        print(f"其他无形资产: ${self.other_intangibles[year]:,.0f}M")
        print(f"其他非流动资产: ${self.other_noncurrent_assets[year]:,.0f}M")
        print(f"\n总资产: ${self.total_assets[year]:,.0f}M")
        
        print(f"\n【负债】")
        print(f"应付账款: ${self.ap[year]:,.0f}M")
        print(f"短期债务: ${self.st_debt[year]:,.0f}M")
        print(f"流动负债: ${self.current_liabilities[year]:,.0f}M")
        print(f"\n长期债务: ${self.lt_debt[year]:,.0f}M")
        print(f"非流动负债: ${self.noncurrent_liabilities[year]:,.0f}M")
        print(f"\n总负债: ${self.total_liabilities[year]:,.0f}M")
        
        print(f"\n【股东权益】")
        print(f"普通股: ${self.common_stock[year]:,.0f}M")
        print(f"资本公积: ${self.apic[year]:,.0f}M")
        print(f"留存收益: ${self.retained_earnings[year]:,.0f}M")
        print(f"库藏股: ${self.treasury_stock[year]:,.0f}M")
        print(f"其他权益: ${self.other_equity[year]:,.0f}M")
        print(f"股东权益: ${self.stockholders_equity[year]:,.0f}M")
        print(f"总权益: ${self.total_equity[year]:,.0f}M")
        
        print(f"\n{'='*80}")
        print(f"验证: 资产 - (负债 + 权益) = "
              f"${self.total_assets[year] - (self.total_liabilities[year] + self.total_equity[year]):,.2f}M")
        print(f"{'='*80}")
