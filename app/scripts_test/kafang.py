import pandas as pd
from collections import Counter
from scipy.stats import chisquare
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(filepath):
    """
    从当前目录下的CSV文件加载数据。
    """
    try:
        data = pd.read_csv(filepath)
        logging.info("数据加载成功。")
        return data
    except Exception as e:
        logging.error(f"从 {filepath} 加载数据失败: {e}")
        raise

def parse_numbers(data, column_name):
    """
    解析DataFrame中的一列，其中每个条目是一串空格分隔的数字。
    """
    try:
        numbers = [int(num) for entry in data[column_name] for num in entry.split()]
        logging.info("数字解析成功。")
        return numbers
    except Exception as e:
        logging.error(f"从列 {column_name} 解析数字失败: {e}")
        raise

def perform_chi_square_test(numbers, n_numbers):
    """
    执行卡方检验，以检查数字分布的均匀性。
    """
    frequency = Counter(numbers)
    observed_frequencies = [frequency.get(i, 0) for i in range(1, n_numbers + 1)]
    expected_frequencies = [len(numbers) / n_numbers] * n_numbers
    chi2_stat, p_value = chisquare(f_obs=observed_frequencies, f_exp=expected_frequencies)
    return chi2_stat, p_value

if __name__ == "__main__":
    # 指定CSV文件路径和包含彩票号码的列名
    filepath = 'combined.csv'  # 根据需要调整文件名
    column_name = 'lotteryDrawResult'  # 根据需要调整列名
    
    # 从CSV文件加载数据
    data = load_data(filepath)
    
    # 从指定列解析数字
    numbers = parse_numbers(data, column_name)
    
    # 假设数字范围为1到35（根据需要调整），执行卡方检验
    chi2_stat, p_value = perform_chi_square_test(numbers, 35)
    
    # 输出卡方检验结果
    logging.info(f"卡方统计量: {chi2_stat}")
    logging.info(f"P值: {p_value}")
