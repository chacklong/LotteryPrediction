# import pandas as pd
# df = pd.read_csv('./LOTTERY_LIST_PAGE_1.csv')
# print(df.head())
# print(df.info())
import pandas as pd
import glob

# 获取所有CSV文件的路径
csv_files = glob.glob('../LOTTERY_LIST_PAGE_*.csv')

# 读取所有的CSV文件并存储在一个列表中
dfs = [pd.read_csv(f) for f in csv_files]

# 合并所有的DataFrame
df = pd.concat(dfs, ignore_index=True)

# 保存合并后的DataFrame到一个新的CSV文件
df.to_csv('combined.csv', index=False)

# import pandas as pd
# import numpy as np
# from collections import Counter

# # 读取CSV文件
# df = pd.read_csv('combined.csv', encoding='ISO-8859-1')

# # 假设你的开奖结果列名为'lotteryDrawResult'，并且每个结果是一个由空格分隔的字符串
# # 我们首先将每个结果转换为一个数字列表，然后分割为前区和后区
# df['lotteryDrawResult'] = df['lotteryDrawResult'].apply(lambda x: list(map(int, x.split())))

# # 创建前区和后区的结果列
# df['front_area'] = df['lotteryDrawResult'].apply(lambda x: x[:5])
# df['back_area'] = df['lotteryDrawResult'].apply(lambda x: x[5:])

# # 展开所有的号码
# front_area_numbers = [number for sublist in df['front_area'].tolist() for number in sublist]
# back_area_numbers = [number for sublist in df['back_area'].tolist() for number in sublist]

# # 计算每个号码的出现频率
# front_area_freq = dict(Counter(front_area_numbers))
# back_area_freq = dict(Counter(back_area_numbers))

# # 输出前区和后区的号码频率
# print("Front area numbers frequency:")
# for k, v in sorted(front_area_freq.items(), key=lambda item: item[1], reverse=True):
#     print(f"Number: {k}, Frequency: {v}")

# print("\nBack area numbers frequency:")
# for k, v in sorted(back_area_freq.items(), key=lambda item: item[1], reverse=True):
#     print(f"Number: {k}, Frequency: {v}")

# # 根据这些频率来预测下一期的开奖号码
# # 这里我们选择频率最高的5个前区号码和2个后区号码，重复这个过程5次
# for i in range(5):
#     next_front_area = [k for k, v in sorted(front_area_freq.items(), key=lambda item: item[1], reverse=True)[:5]]
#     next_back_area = [k for k, v in sorted(back_area_freq.items(), key=lambda item: item[1], reverse=True)[:2]]
#     print(f"\nPrediction {i+1}:")
#     print("Front area numbers:", sorted(next_front_area))
#     print("Back area numbers:", sorted(next_back_area))
