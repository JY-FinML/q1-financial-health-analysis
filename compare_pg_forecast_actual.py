"""
P&G预测结果与实际值对比
输出2024和2025年的利润表和资产负债表，并计算差异
"""
from pg_forecast.forecaster import PGForecaster
from pg_forecast.data_loader import load_all_data, get_value
from pg_forecast.config import YEAR_END_DATES


def format_value(value):
    """格式化数值显示"""
    return f"${value:,.0f}M"

def format_diff(forecast, actual):
    """计算并格式化差异"""
    if actual == 0:
        return "N/A", "N/A"
    diff = forecast - actual
    diff_pct = (diff / actual) * 100
    return f"${diff:,.0f}M", f"{diff_pct:.2f}%"


def print_income_statement_comparison():
    """打印利润表对比"""
    print("\n" + "="*120)
    print("利润表对比 (Income Statement)")
    print("="*120)
    
    # 运行预测
    forecaster = PGForecaster()
    forecaster.run_forecast()
    
    # 加载实际数据
    all_data = load_all_data()
    is_actual = all_data['income_statement']
    
    # 定义要对比的项目
    items = [
        ('总收入', 'revenue', 'Total Revenue'),
        ('营业成本', 'cogs', 'Cost Of Revenue'),
        ('毛利润', 'gross_profit', 'Gross Profit'),
        ('营业费用', 'operating_expenses', 'Operating Expense'),
        ('EBIT', 'ebit', 'EBIT'),
        ('折旧', 'depreciation', 'Reconciled Depreciation'),
        ('EBITDA', 'ebitda', 'EBITDA'),
        ('利息费用', 'interest_expense', 'Interest Expense'),
        ('利息收入', 'interest_income', 'Interest Income'),
        ('税前利润', 'ebt', 'Pretax Income'),
        ('所得税', 'tax', 'Tax Provision'),
        ('净利润', 'net_income', 'Net Income'),
    ]
    
    # 打印2024年对比
    print("\n【2024年预测 vs 实际】")
    print(f"{'项目':<20} {'预测值':>15} {'实际值':>15} {'差异':>15} {'差异%':>10}")
    print("-"*120)
    
    date_2024 = YEAR_END_DATES[2024]
    for name_cn, attr, name_en in items:
        forecast_val = getattr(forecaster, attr)[1]  # Year 1
        actual_val = get_value(is_actual, name_en, date_2024)
        diff, diff_pct = format_diff(forecast_val, actual_val)
        
        print(f"{name_cn:<20} {format_value(forecast_val):>15} {format_value(actual_val):>15} {diff:>15} {diff_pct:>10}")
    
    # 打印2025年对比
    print("\n【2025年预测 vs 实际】")
    print(f"{'项目':<20} {'预测值':>15} {'实际值':>15} {'差异':>15} {'差异%':>10}")
    print("-"*120)
    
    date_2025 = YEAR_END_DATES[2025]
    for name_cn, attr, name_en in items:
        forecast_val = getattr(forecaster, attr)[2]  # Year 2
        actual_val = get_value(is_actual, name_en, date_2025)
        diff, diff_pct = format_diff(forecast_val, actual_val)
        
        print(f"{name_cn:<20} {format_value(forecast_val):>15} {format_value(actual_val):>15} {diff:>15} {diff_pct:>10}")


def print_balance_sheet_comparison():
    """打印资产负债表对比"""
    print("\n" + "="*120)
    print("资产负债表对比 (Balance Sheet)")
    print("="*120)
    
    # 运行预测
    forecaster = PGForecaster()
    forecaster.run_forecast()
    
    # 加载实际数据
    all_data = load_all_data()
    bs_actual = all_data['balance_sheet']
    
    # 定义要对比的项目
    items = [
        # 资产
        ('【资产】', None, None),
        ('现金', 'cash', 'Cash And Cash Equivalents'),
        ('应收账款', 'ar', 'Accounts Receivable'),
        ('存货', 'inventory', 'Inventory'),
        ('流动资产', 'current_assets', 'Current Assets'),
        ('', None, None),
        ('固定资产总额', 'gross_ppe', 'Gross PPE'),
        ('累计折旧', 'acc_depreciation', 'Accumulated Depreciation'),
        ('固定资产净值', 'net_ppe', 'Net PPE'),
        ('', None, None),
        ('商誉', 'goodwill', 'Goodwill'),
        ('其他无形资产', 'other_intangibles', 'Other Intangible Assets'),
        ('其他非流动资产', 'other_noncurrent_assets', 'Other Non Current Assets'),
        ('总资产', 'total_assets', 'Total Assets'),
        ('', None, None),
        # 负债
        ('【负债】', None, None),
        ('应付账款', 'ap', 'Accounts Payable'),
        ('短期债务', 'st_debt', 'Current Debt'),
        ('流动负债', 'current_liabilities', 'Current Liabilities'),
        ('', None, None),
        ('长期债务', 'lt_debt', 'Long Term Debt'),
        ('总债务', 'total_debt', 'Total Debt'),
        ('非流动负债', 'noncurrent_liabilities', 'Total Non Current Liabilities Net Minority Interest'),
        ('总负债', 'total_liabilities', 'Total Liabilities Net Minority Interest'),
        ('', None, None),
        # 权益
        ('【股东权益】', None, None),
        ('普通股', 'common_stock', 'Common Stock'),
        ('资本公积', 'apic', 'Additional Paid In Capital'),
        ('留存收益', 'retained_earnings', 'Retained Earnings'),
        ('库藏股', 'treasury_stock', 'Treasury Stock'),
        ('其他权益', 'other_equity', 'Other Equity Interest'),
        ('股东权益', 'stockholders_equity', 'Stockholders Equity'),
        ('总权益', 'total_equity', 'Total Equity Gross Minority Interest'),
    ]
    
    # 打印2024年对比
    print("\n【2024年预测 vs 实际】")
    print(f"{'项目':<20} {'预测值':>15} {'实际值':>15} {'差异':>15} {'差异%':>10}")
    print("-"*120)
    
    date_2024 = YEAR_END_DATES[2024]
    for name_cn, attr, name_en in items:
        if attr is None:
            print(f"{name_cn}")
            continue
        
        forecast_val = getattr(forecaster, attr)[1]  # Year 1
        actual_val = get_value(bs_actual, name_en, date_2024)
        
        # 累计折旧取绝对值
        if attr == 'acc_depreciation':
            actual_val = abs(actual_val)
        
        diff, diff_pct = format_diff(forecast_val, actual_val)
        print(f"{name_cn:<20} {format_value(forecast_val):>15} {format_value(actual_val):>15} {diff:>15} {diff_pct:>10}")
    
    # 打印2025年对比
    print("\n【2025年预测 vs 实际】")
    print(f"{'项目':<20} {'预测值':>15} {'实际值':>15} {'差异':>15} {'差异%':>10}")
    print("-"*120)
    
    date_2025 = YEAR_END_DATES[2025]
    for name_cn, attr, name_en in items:
        if attr is None:
            print(f"{name_cn}")
            continue
        
        forecast_val = getattr(forecaster, attr)[2]  # Year 2
        actual_val = get_value(bs_actual, name_en, date_2025)
        
        # 累计折旧取绝对值
        if attr == 'acc_depreciation':
            actual_val = abs(actual_val)
        
        diff, diff_pct = format_diff(forecast_val, actual_val)
        print(f"{name_cn:<20} {format_value(forecast_val):>15} {format_value(actual_val):>15} {diff:>15} {diff_pct:>10}")


def print_summary_statistics():
    """打印汇总统计"""
    print("\n" + "="*120)
    print("预测准确性汇总")
    print("="*120)
    
    forecaster = PGForecaster()
    forecaster.run_forecast()
    
    all_data = load_all_data()
    is_actual = all_data['income_statement']
    bs_actual = all_data['balance_sheet']
    
    # 关键指标
    key_metrics = [
        ('2024年收入', forecaster.revenue[1], get_value(is_actual, 'Total Revenue', YEAR_END_DATES[2024])),
        ('2024年EBIT', forecaster.ebit[1], get_value(is_actual, 'EBIT', YEAR_END_DATES[2024])),
        ('2024年净利润', forecaster.net_income[1], get_value(is_actual, 'Net Income', YEAR_END_DATES[2024])),
        ('2024年总资产', forecaster.total_assets[1], get_value(bs_actual, 'Total Assets', YEAR_END_DATES[2024])),
        ('2024年股东权益', forecaster.stockholders_equity[1], get_value(bs_actual, 'Stockholders Equity', YEAR_END_DATES[2024])),
        ('', 0, 0),
        ('2025年收入', forecaster.revenue[2], get_value(is_actual, 'Total Revenue', YEAR_END_DATES[2025])),
        ('2025年EBIT', forecaster.ebit[2], get_value(is_actual, 'EBIT', YEAR_END_DATES[2025])),
        ('2025年净利润', forecaster.net_income[2], get_value(is_actual, 'Net Income', YEAR_END_DATES[2025])),
        ('2025年总资产', forecaster.total_assets[2], get_value(bs_actual, 'Total Assets', YEAR_END_DATES[2025])),
        ('2025年股东权益', forecaster.stockholders_equity[2], get_value(bs_actual, 'Stockholders Equity', YEAR_END_DATES[2025])),
    ]
    
    print(f"\n{'关键指标':<25} {'预测值':>15} {'实际值':>15} {'差异%':>10} {'状态':>10}")
    print("-"*120)
    
    for name, forecast_val, actual_val in key_metrics:
        if name == '':
            print()
            continue
        
        if actual_val != 0:
            diff_pct = ((forecast_val - actual_val) / actual_val) * 100
            
            # 判断准确性
            if abs(diff_pct) < 1:
                status = "✓✓ 优秀"
            elif abs(diff_pct) < 5:
                status = "✓ 良好"
            elif abs(diff_pct) < 10:
                status = "○ 可接受"
            else:
                status = "✗ 待改进"
            
            print(f"{name:<25} {format_value(forecast_val):>15} {format_value(actual_val):>15} {diff_pct:>9.2f}% {status:>10}")


def main():
    """主函数"""
    print("\n" + "="*120)
    print("P&G财务预测结果与实际值对比分析")
    print("="*120)
    
    # 打印利润表对比
    print_income_statement_comparison()
    
    # 打印资产负债表对比
    print_balance_sheet_comparison()
    
    # 打印汇总统计
    print_summary_statistics()
    
    print("\n" + "="*120)
    print("分析完成")
    print("="*120 + "\n")


if __name__ == "__main__":
    main()
