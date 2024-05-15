import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor

# 加载数据
df = pd.read_csv('combined.csv', encoding='ISO-8859-1')

# 处理开奖结果
df['lotteryDrawResult'] = df['lotteryDrawResult'].apply(lambda x: [int(num) for num in x.split(' ')])

# 确保所有的开奖结果都有相同数量的数字
assert df['lotteryDrawResult'].apply(len).nunique() == 1

# 创建日期特征
df['lotteryDrawTime'] = pd.to_datetime(df['lotteryDrawTime'])
df['year'] = df['lotteryDrawTime'].dt.year
df['month'] = df['lotteryDrawTime'].dt.month
df['day'] = df['lotteryDrawTime'].dt.day
df['day_of_week'] = df['lotteryDrawTime'].dt.dayofweek

# 创建前区和后区的结果列
df['front_area'] = df['lotteryDrawResult'].apply(lambda x: x[:5])
df['back_area'] = df['lotteryDrawResult'].apply(lambda x: x[5:])

# 创建前区和后区的目标变量
y_front = pd.DataFrame(df['front_area'].to_list(), columns=[f'front_num_{i}' for i in range(1, 6)])
y_back = pd.DataFrame(df['back_area'].to_list(), columns=[f'back_num_{i}' for i in range(1, 3)])

# 分割数据为训练集和测试集
X = df[['year', 'month', 'day', 'day_of_week']]
X_train, X_test, y_front_train, y_front_test, y_back_train, y_back_test = train_test_split(X, y_front, y_back, test_size=0.2, random_state=42)

# 创建前区和后区的模型
model_front = MultiOutputRegressor(RandomForestRegressor(random_state=42))
model_back = MultiOutputRegressor(RandomForestRegressor(random_state=42))

# 设置参数网格
param_grid = {'estimator__n_estimators': [50, 100, 200], 'estimator__max_depth': [None, 10, 20, 30]}

# 创建网格搜索对象
grid_search_front = GridSearchCV(model_front, param_grid, cv=5)
grid_search_back = GridSearchCV(model_back, param_grid, cv=5)

# 训练前区和后区的模型
grid_search_front.fit(X_train, y_front_train)
grid_search_back.fit(X_train, y_back_train)

# 打印最佳参数
print("Best parameters for front area: ", grid_search_front.best_params_)
print("Best parameters for back area: ", grid_search_back.best_params_)

# 预测前区和后区的结果
y_front_pred = grid_search_front.predict(X_test)
y_back_pred = grid_search_back.predict(X_test)

# 四舍五入预测结果到最近的整数
y_front_pred = np.round(y_front_pred).astype(int)
y_back_pred = np.round(y_back_pred).astype(int)

# 组合预测结果
y_pred = np.concatenate((y_front_pred, y_back_pred), axis=1)

# 查看预测结果
print(y_pred)
