# LotteryPredictionSystem2/app/analysis/model/eda_frame.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils import resample
import logging
import os

def load_prepare_data(filepath):
    logging.info(f"Loading data from {filepath}...")
    data = pd.read_csv(filepath)
    data[['num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7']] = data['lotteryDrawResult'].str.split(expand=True)
    for col in ['num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7']:
        data[col] = pd.to_numeric(data[col])
    logging.info("Data prepared for training.")
    return data

def balance_data(data, target='num1'):
    class_counts = data[target].value_counts()
    max_size = class_counts.max()
    lst = [data]
    for class_index, group in data.groupby(target):
        lst.append(group.sample(max_size-len(group), replace=True))
    data = pd.concat(lst)
    logging.info("Data balanced.")
    return data

def split_data(data):
    X = data[['num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7']]
    y = data['num1']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    logging.info("Data split into train and test sets.")
    return X_train, X_test, y_train, y_test

def train_evaluate(X_train, X_test, y_train, y_test):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=1)
    logging.info(f"Model trained successfully with accuracy: {accuracy}")
    return model, accuracy, report

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='model_training.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    data_dir = 'app/data/test'  # 设置数据文件夹路径
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(data_dir, filename)
            try:
                data = load_prepare_data(file_path)
                X_train, X_test, y_train, y_test = split_data(data)
                model, accuracy, report = train_evaluate(X_train, X_test, y_train, y_test)
                logging.info(f"Classification Report for {filename}: \n{report}")
            except Exception as e:
                logging.error(f"An error occurred while processing {filename}: {e}")
