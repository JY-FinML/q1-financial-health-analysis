"""
P&G财务预测 - 主运行脚本
使用现金预算法（与forecast_model相同的计算逻辑）
"""
from pg_forecast.forecaster import PGForecaster


def main():
    print("\n" + "="*80)
    print("P&G财务预测系统（现金预算法）")
    print("使用与forecast_model相同的计算逻辑")
    print("="*80)
    
    # 创建预测器
    forecaster = PGForecaster()
    
    # 打印Year 0数据
    print("\n" + "="*80)
    print("Year 0 (2023) - 基准年数据")
    print("="*80)
    print(f"\n【利润表】")
    print(f"收入: ${forecaster.revenue[0]:,.0f}M")
    print(f"COGS: ${forecaster.cogs[0]:,.0f}M")
    print(f"毛利润: ${forecaster.gross_profit[0]:,.0f}M")
    print(f"运营费用: ${forecaster.operating_expenses[0]:,.0f}M")
    print(f"EBIT: ${forecaster.ebit[0]:,.0f}M")
    print(f"折旧: ${forecaster.depreciation[0]:,.0f}M")
    print(f"EBITDA: ${forecaster.ebitda[0]:,.0f}M")
    print(f"税前利润: ${forecaster.ebt[0]:,.0f}M")
    print(f"净利润: ${forecaster.net_income[0]:,.0f}M")
    
    print(f"\n【资产负债表】")
    print(f"总资产: ${forecaster.total_assets[0]:,.0f}M")
    print(f"现金: ${forecaster.cash[0]:,.0f}M")
    print(f"总负债: ${forecaster.total_liabilities[0]:,.0f}M")
    print(f"股东权益: ${forecaster.stockholders_equity[0]:,.0f}M")
    print(f"总权益: ${forecaster.total_equity[0]:,.0f}M")
    print(f"平衡检查: 资产 - (负债 + 权益) = ${forecaster.total_assets[0] - forecaster.total_liabilities[0] - forecaster.total_equity[0]:,.0f}M")
    
    print(f"\n【现金流】")
    print(f"经营现金流: ${forecaster.operating_cf[0]:,.0f}M")
    print(f"资本支出: ${forecaster.capex[0]:,.0f}M")
    print(f"自由现金流: ${forecaster.free_cf[0]:,.0f}M")
    print(f"股息: ${forecaster.dividends[0]:,.0f}M")
    
    # 运行预测
    forecaster.run_forecast()
    
    # 打印详细资产负债表
    for year in [1, 2]:
        forecaster.print_detailed_balance_sheet(year)
    
    # 打印利润表对比
    print("\n" + "="*80)
    print("利润表总结")
    print("="*80)
    print(f"{'项目':<30} {'Year 0 (2023)':>15} {'Year 1 (2024)':>15} {'Year 2 (2025)':>15}")
    print("-"*80)
    
    items = [
        ('收入', forecaster.revenue),
        ('COGS', forecaster.cogs),
        ('毛利润', forecaster.gross_profit),
        ('营业费用', forecaster.operating_expenses),
        ('EBIT', forecaster.ebit),
        ('折旧', forecaster.depreciation),
        ('EBITDA', forecaster.ebitda),
        ('利息费用', forecaster.interest_expense),
        ('税前利润', forecaster.ebt),
        ('税', forecaster.tax),
        ('净利润', forecaster.net_income),
    ]
    
    for name, values in items:
        print(f"{name:<30} ${values[0]:>13,.0f}M ${values[1]:>13,.0f}M ${values[2]:>13,.0f}M")
    
    # 打印现金流总结
    print("\n" + "="*80)
    print("现金流量表总结")
    print("="*80)
    print(f"{'项目':<30} {'Year 1 (2024)':>15} {'Year 2 (2025)':>15}")
    print("-"*80)
    
    cf_items = [
        ('经营现金流', forecaster.operating_cf),
        ('资本支出', forecaster.capex),
        ('自由现金流', forecaster.free_cf),
        ('投资现金流', forecaster.investing_cf),
        ('融资现金流', forecaster.financing_cf),
        ('股息支付', forecaster.dividends),
        ('股票回购', forecaster.stock_repurchase),
    ]
    
    for name, values in cf_items:
        if name == '资本支出':
            print(f"{name:<30} ${-values[1]:>13,.0f}M ${-values[2]:>13,.0f}M")
        elif name in ['股息支付', '股票回购']:
            print(f"{name:<30} ${-values[1]:>13,.0f}M ${-values[2]:>13,.0f}M")
        else:
            print(f"{name:<30} ${values[1]:>13,.0f}M ${values[2]:>13,.0f}M")
    
    print("\n" + "="*80)
    
    return forecaster


if __name__ == "__main__":
    forecaster = main()
