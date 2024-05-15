import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor

# 加载数据
df = pd.read_csv('combined.csv', encoding='ISO-8859-1')

# 处理开奖结果
df['lotteryDrawResult'] = df['lotteryDrawResult'].apply(lambda x: [int(num) for num in x.split(' ')])

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
models = [
    ("XGBRegressor", MultiOutputRegressor(XGBRegressor(objective='reg:squarederror', random_state=42))),
    ("LinearRegression", MultiOutputRegressor(LinearRegression())),
    ("RandomForestRegressor", MultiOutputRegressor(RandomForestRegressor(random_state=42))),
    ("SVR", MultiOutputRegressor(SVR())),
    ("KNeighborsRegressor", MultiOutputRegressor(KNeighborsRegressor())),
    ("DecisionTreeRegressor", MultiOutputRegressor(DecisionTreeRegressor(random_state=42))),
    ("GradientBoostingRegressor", MultiOutputRegressor(GradientBoostingRegressor(random_state=42)))
]

# 设置参数网格
param_grids = {
    "XGBRegressor": {'estimator__n_estimators': [100, 200, 300], 'estimator__max_depth': [3, 5, 7]},
    "LinearRegression": {},
    "RandomForestRegressor": {'estimator__n_estimators': [100, 200, 300], 'estimator__max_depth': [3, 5, 7]},
    "SVR": {'estimator__kernel': ['linear', 'poly', 'rbf', 'sigmoid']},
    "KNeighborsRegressor": {'estimator__n_neighbors': [3, 5, 7]},
    "DecisionTreeRegressor": {'estimator__max_depth': [3, 5, 7]},
    "GradientBoostingRegressor": {'estimator__n_estimators': [100, 200, 300], 'estimator__max_depth': [3, 5, 7]}
}

# 训练模型并预测
results = []
for name, model in models:
    print(f"Training and predicting with {name}...")
    param_grid = param_grids[name]
    grid_search = GridSearchCV(model, param_grid, cv=5)
    grid_search.fit(X_train, y_front_train)
    grid_search.fit(X_train, y_back_train)
    y_front_pred = grid_search.predict(X_test)
    y_back_pred = grid_search.predict(X_test)

    # 处理模型输出的格式
    y_front_pred = np.round(y_front_pred).astype(int)
    y_back_pred = np.round(y_back_pred).astype(int)

    # 将前后区号码合并
    y_pred = np.concatenate((y_front_pred, y_back_pred), axis=1)
    rmse_front = sqrt(mean_squared_error(y_front_test, y_front_pred))
    rmse_back = sqrt(mean_squared_error(y_back_test, y_back_pred))
    results.append((name, y_pred, rmse_front, rmse_back))

# 打印结果
for name, y_pred, rmse_front, rmse_back in results:
    print(f"Model: {name}")
    print("Predicted numbers:")
    print(y_pred)
    print(f"RMSE for front area: {rmse_front}")
    print(f"RMSE for back area: {rmse_back}")
