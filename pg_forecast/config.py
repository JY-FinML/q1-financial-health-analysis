"""
配置文件
定义预测参数和数据路径
"""

# 数据路径
DATA_DIR = "data/ProcterGamble"
BALANCE_SHEET_FILE = f"{DATA_DIR}/balance sheet.csv"
INCOME_STATEMENT_FILE = f"{DATA_DIR}/income statement.csv"
CASH_FLOW_FILE = f"{DATA_DIR}/cash flow.csv"

# 预测年份
BASE_YEARS = [2022, 2023]  # 使用2022和2023年的历史数据
FORECAST_YEARS = [2024, 2025]  # 预测2024和2025年
ALL_YEARS = BASE_YEARS + FORECAST_YEARS

# 日期格式（P&G使用财年结束日期，6月30日）
YEAR_END_DATES = {
    2022: "2022-06-30",
    2023: "2023-06-30",
    2024: "2024-06-30",
    2025: "2025-06-30"
}
