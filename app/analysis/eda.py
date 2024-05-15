# /app/analysis/eda.py
import pandas as pd
from collections import Counter
import logging
from ..config import ANALYSIS_DATA_FILE

def load_data():
    """
    从配置文件指定的CSV文件加载数据。
    将 'lotteryDrawTime' 转换为 datetime 格式以便后续分析。
    """
    try:
        data = pd.read_csv(ANALYSIS_DATA_FILE)
        data['lotteryDrawTime'] = pd.to_datetime(data['lotteryDrawTime'])
        logging.info("数据加载成功。")
        return data
    except Exception as e:
        logging.error(f"从 {ANALYSIS_DATA_FILE} 加载数据出错: {e}")
        raise

def parse_numbers(data):
    """
    解析彩票开奖结果，将结果分解为数字列表。
    """
    all_numbers = [num for sublist in data['lotteryDrawResult'].str.split() for num in sublist]
    return all_numbers

def calculate_frequencies(numbers):
    """
    计算列表中每个数字的频率和概率。
    """
    frequency = Counter(numbers)
    total_counts = sum(frequency.values())
    probability = {k: float(f"{v / total_counts:.4f}") for k, v in frequency.items()}
    return frequency, probability

def get_frequency_and_probability():
    """
    获取数据集中前30条数据的数字频率和概率。
    """
    data = load_data()
    last_30_data = data.head(30)
    numbers = parse_numbers(last_30_data)
    frequency, probability = calculate_frequencies(numbers)
    return frequency, probability

def time_trend_analysis(data):
    """
    通过设置 'lotteryDrawTime' 为索引并按月重采样，分析时间趋势。
    计算每月数字的频率。
    """
    if 'lotteryDrawTime' not in data.columns:
        logging.error("数据中缺少 'lotteryDrawTime' 列")
        raise ValueError("数据中缺少 'lotteryDrawTime' 列")

    data = data.set_index('lotteryDrawTime')
    logging.info(f"已将 'lotteryDrawTime' 设置为索引，索引类型现在是: {type(data.index)}")

    if not isinstance(data.index, pd.DatetimeIndex):
        logging.error("设置索引后索引类型不是 DatetimeIndex，出现问题")
        raise TypeError("设置索引后索引类型不是 DatetimeIndex，出现问题")

    try:
        monthly_data = data.resample('M')['lotteryDrawResult'].agg(lambda x: [num for sublist in x.str.split() for num in sublist])
        monthly_frequencies = monthly_data.apply(Counter)
        logging.info("时间趋势分析完成")
        return monthly_frequencies.to_dict()
    except Exception as e:
        logging.error(f"进行时间趋势分析时出错: {e}")
        raise

def hot_and_cold_numbers(data):
    """
    从数据集中确定出现频率最高的（热号）和最低的（冷号）数字。
    """
    all_numbers = [num for sublist in data['lotteryDrawResult'].str.split() for num in sublist]
    frequency = Counter(all_numbers)
    sorted_frequency = dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True))
    hot_numbers = list(sorted_frequency.items())[:5]
    cold_numbers = list(sorted_frequency.items())[-5:]
    return {'hot_numbers': hot_numbers, 'cold_numbers': cold_numbers}
