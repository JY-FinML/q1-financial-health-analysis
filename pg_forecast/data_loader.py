"""
数据加载模块
从CSV文件读取历史财务数据
"""
import csv
from typing import Dict, List
from .config import BALANCE_SHEET_FILE, INCOME_STATEMENT_FILE, CASH_FLOW_FILE


def load_csv_data(filepath: str) -> Dict[str, Dict[str, float]]:
    """
    加载CSV文件，返回字典格式的数据
    
    返回格式:
    {
        'Account Name': {
            '2022-06-30': value,
            '2023-06-30': value,
            ...
        }
    }
    """
    data = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # 第一行是日期列标题
        dates = headers[1:]  # 跳过第一列（账户名称列）
        
        for row in reader:
            if not row or not row[0]:
                continue
                
            account_name = row[0]
            values = {}
            
            for i, date in enumerate(dates, start=1):
                try:
                    # 尝试转换为浮点数
                    value = float(row[i]) if row[i] and row[i].strip() else 0.0
                    values[date] = value
                except (ValueError, IndexError):
                    values[date] = 0.0
            
            data[account_name] = values
    
    return data


def load_all_data() -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    加载所有财务报表数据
    
    返回格式:
    {
        'balance_sheet': {...},
        'income_statement': {...},
        'cash_flow': {...}
    }
    """
    return {
        'balance_sheet': load_csv_data(BALANCE_SHEET_FILE),
        'income_statement': load_csv_data(INCOME_STATEMENT_FILE),
        'cash_flow': load_csv_data(CASH_FLOW_FILE)
    }


def get_value(data: Dict[str, Dict[str, float]], account: str, date: str, default: float = 0.0) -> float:
    """
    安全获取账户值
    """
    if account in data and date in data[account]:
        return data[account][date]
    return default


def get_historical_values(data: Dict[str, Dict[str, float]], account: str, dates: List[str]) -> List[float]:
    """
    获取某个账户的历史值列表
    """
    return [get_value(data, account, date) for date in dates]
