# app/analysis/eda.py
import pandas as pd
from collections import Counter
import logging
from ..config import ANALYSIS_DATA_FILE
from pathlib import Path

def load_data(file_path):
    """
    载入CSV数据文件。

    参数：
        file_path (str): CSV文件路径
    """
    try:
        data = pd.read_csv(file_path)
        logging.info(f"数据成功载入: {file_path}")
        return data
    except FileNotFoundError:
        logging.error(f"文件未找到: {file_path}")
        raise
    except Exception as e:
        logging.error(f"在载入数据时发生错误: {e}")
        raise

def parse_numbers(data):
    """
    解析数据中的号码，将所有号码分离并展平成一个列表。

    参数:
        data (DataFrame): 包含彩票号码的数据框

    返回：
        list: 展平后的号码列表
    """
    all_numbers = [num for sublist in data['lotteryDrawResult'].str.split() for num in sublist]
    return all_numbers

def calculate_frequencies(numbers):
    """
    计算号码的频率和概率。
    
    参数：
        numbers (list): 号码列表
    
    返回:
        tuple: 包含两个字典，分别是号码的频率和概率
    """
    frequency = Counter(numbers)
    total_counts = sum(frequency.values())
    probability = {k: v / total_counts for k, v in frequency.items()}
    return frequency, probability

def process_data():
    """
    处理数据文件，计算并打印每个号码在最近30期内的频率和概率。

    使用从配置文件引入的文件路径。
    """
    file_path = Path(ANALYSIS_DATA_FILE)
    data = load_data(file_path)
    last_30_draws = data.head(30)
    numbers = parse_numbers(last_30_draws)
    frequency, probability = calculate_frequencies(numbers)
    print(f"最近30期中每个号码出现的频率: {frequency}")
    print(f"最近30期中每个号码出现的概率: {probability}")
    logging.info(f"最近30期中每个号码出现的频率: {frequency}")
    logging.info(f"最近30期中每个号码出现的概率: {probability}")

# 如果这个脚本被直接运行，执行process_data
if __name__ == "__main__":
    process_data()

# =======================================================================================

import pandas as pd
from collections import Counter
import logging
from ..config import ANALYSIS_DATA_FILE

def load_data():
    """加载数据并将时间列转换为 datetime 类型，方便后续处理。"""
    try:
        data = pd.read_csv(ANALYSIS_DATA_FILE)
        data['lotteryDrawTime'] = pd.to_datetime(data['lotteryDrawTime'])
        return data
    except Exception as e:
        logging.error(f"加载数据失败: {e}")
        raise

def parse_lottery_numbers(data):
    """将彩票开奖结果分割为前区和后区数字。"""
    data['front_area'] = data['lotteryDrawResult'].apply(lambda x: [int(num) for num in x.split()[:5]])
    data['back_area'] = data['lotteryDrawResult'].apply(lambda x: [int(num) for num in x.split()[5:]])
    return data

def frequency_analysis(numbers):
    """计算数字的出现频率。"""
    return Counter(numbers)

def area_frequency_analysis(data, area='front_area'):
    """分析指定区域（前区或后区）的数字频率。"""
    all_numbers = [num for sublist in data[area] for num in sublist]
    return frequency_analysis(all_numbers)

def time_trend_analysis(data, area='front_area'):
    """按时间趋势分析指定区域的数字频率。"""
    data['year'] = data['lotteryDrawTime'].dt.year
    data['month'] = data['lotteryDrawTime'].dt.month
    return data.groupby('year')[area].apply(lambda x: Counter([num for sublist in x for num in sublist]))

def consecutive_analysis(data, area='front_area'):
    """分析连号的出现频率和模式。"""
    def count_consecutive(nums):
        nums = sorted(nums)
        return sum(1 for i in range(len(nums) - 1) if nums[i] + 1 == nums[i + 1])
    consecutive_counts = data[area].apply(count_consecutive)
    return sum(consecutive_counts)

def skip_analysis(data, area='front_area'):
    """分析指定区域的跳号模式。"""
    def count_skips(nums):
        nums = sorted(nums)
        return Counter(nums[i + 1] - nums[i] for i in range(len(nums) - 1) if nums[i + 1] - nums[i] > 1)
    skips = data[area].apply(count_skips)
    return sum(skips, Counter())

def sum_analysis(data, area='front_area'):
    """分析指定区域的和值。"""
    sums = data[area].apply(sum)
    return sums.describe()

# 使用示例
if __name__ == "__main__":
    data = load_data()
    data = parse_lottery_numbers(data)
    front_frequency = area_frequency_analysis(data, 'front_area')
    back_frequency = area_frequency_analysis(data, 'back_area')
    yearly_trends_front = time_trend_analysis(data, 'front_area')
    consecutive_front = consecutive_analysis(data, 'front_area')
    skips_front = skip_analysis(data, 'front_area')
    sums_front = sum_analysis(data, 'front_area')

    # 输出分析结果
    print("前区频率分析:", front_frequency)
    print("后区频率分析:", back_frequency)
    print("前区年度趋势分析:", yearly_trends_front)
    print("前区连号统计:", consecutive_front)
    print("前区跳号统计:", skips_front)
    print("前区和值统计:", sums_front)
