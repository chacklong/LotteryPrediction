# 读取数据
# data = pd.read_csv(r'C:\Users\Administrator\codeFiles\LotteryPredictionSystem2\tests\test.csv')
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report
from sklearn.multioutput import MultiOutputClassifier
import numpy as np
import logging

# 设置日志配置，以便在运行过程中输出有用的信息
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 加载数据并进行初步的处理
logging.info("正在加载数据...")
data = pd.read_csv(r'C:\Users\Administrator\codeFiles\LotteryPredictionSystem2\tests\test.csv')
data['numbers'] = data['lotteryDrawResult'].str.split()
data['main_numbers'] = data['numbers'].apply(lambda x: x[:5])
data['special_numbers'] = data['numbers'].apply(lambda x: x[5:])

# 转换数据类型，并进行特征工程
logging.info("转换数据类型并开始进行特征工程...")
main_numbers_df = pd.DataFrame(data['main_numbers'].tolist(), columns=['Main1', 'Main2', 'Main3', 'Main4', 'Main5']).apply(pd.to_numeric)
special_numbers_df = pd.DataFrame(data['special_numbers'].tolist(), columns=['Special1', 'Special2']).apply(pd.to_numeric)

for window in [3, 5, 10]:
    main_numbers_df[f'rolling_mean_{window}'] = main_numbers_df['Main1'].rolling(window=window).mean()
    main_numbers_df[f'rolling_std_{window}'] = main_numbers_df['Main1'].rolling(window=window).std()

# 准备模型输入数据
X_main = main_numbers_df.drop(['Main1', 'Main2', 'Main3', 'Main4', 'Main5'], axis=1)
y_main = main_numbers_df[['Main1', 'Main2', 'Main3', 'Main4', 'Main5']]
X_train_main, X_test_main, y_train_main, y_test_main = train_test_split(X_main, y_main, test_size=0.2, random_state=42)

# 设置多输出分类器，并进行模型训练
logging.info("配置多输出分类器并进行模型训练...")
model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
model.fit(X_train_main, y_train_main)
logging.info("模型训练完成。")

# 进行预测，并生成每个输出的分类报告
predictions = model.predict(X_test_main)
logging.info("生成分类报告...")
def multioutput_classification_report(y_true, y_pred):
    for i in range(y_true.shape[1]):
        logging.info(f"输出 {i+1} 的分类报告:")
        print(classification_report(y_true.iloc[:, i], y_pred[:, i], zero_division=0))

multioutput_classification_report(y_test_main, predictions)
