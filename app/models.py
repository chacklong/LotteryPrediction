# app/models.py
import json, requests, logging
from pathlib import Path
from .config import HEADERS
import pandas as pd
import requests
import glob
import re
import os
from typing import Tuple

def fetch_data(url, params):
    try:
        response =  requests.get(url, headers=HEADERS,params=params)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        logging.error(f"HTTP请求失败:{e}")
    except requests.RequestException as e:
        logging.error(f"请求异常:{e}")
    except Exception as e:
        logging.error(f"未知错误:{e}")
    return None

def fetch_all_pages(url, params):
    page = 1
    data = fetch_data(url, params)
    if data and data['value']:
        max_page = data['value'].get('pages', 1)
        save_data(data, page)
        # load_json_and_save_to_csv()
        logging.info(f"Data obtained for page {page}.")
        page += 1

        while page <= max_page:
            params['pageNo'] = page
            data = fetch_data(url, params)
            if data and data['value']:
                save_data(data, page)
                logging.info(f"Data obtained for page {page}.")
                page += 1
            else:
                logging.info(f"No more data available after page {page - 1}.")
                break
    else:
        logging.info("No data obtained from the first request.")

def save_data(data, page, data_directory=Path(__file__).resolve().parent / 'data'):
    # Create data directory if it doesn't exist
    data_directory.mkdir(parents=True, exist_ok=True)

    # Save data to a JSON file, with page number in the file name
    file_path = data_directory / f"lottery_page_{page}.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    logging.info(f"Data saved to {file_path}")

def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    cleaning_stats = {}
    original_row_count = len(df)
    df = df.dropna()
    cleaning_stats['removed_rows_due_to_NaN'] = original_row_count - len(df)
    original_row_count = len(df)  # Update original count after dropping NaNs
    df = df.drop_duplicates(subset=['lotteryDrawNum'])
    cleaning_stats['removed_rows_due_to_duplicates'] = original_row_count - len(df)
    cleaning_stats['remaining_rows'] = len(df)
    cleaning_stats['NaN_counts'] = df.isnull().sum().to_dict()  # Count NaNs in each column

    return df, cleaning_stats

def concatenate_and_delete_files(pattern: list, output_filename: list):
    # 处理每个模式和对应的输出文件名
    for pattern, output_filename in zip(pattern, output_filename):
        logging.info(f"开始合并符合模式 {pattern} 的文件...")
        
        # 初始化空列表， 存储DataFrame
        dfs = []
        files_to_delete = []

        for csv_filename in glob.glob(pattern):
            try:
                # 将csv文件内容读入一个DataFrame
                df = pd.read_csv(csv_filename)
                dfs.append(df)
                files_to_delete.append(csv_filename)
            except pd.errors.EmptyDataError:
                logging.error(f"跳过空文件：{csv_filename}")
            except Exception as e:
                logging.error(f"读取文件 {csv_filename} 时出错：{e}. 跳过该文件")

        if dfs:
            #  合并列表中的所有DataFrame
            df_all = pd.concat(dfs, ignore_index=True)
            # 将合并后的DataFrame保存到新的csv文件中
            df_all.to_csv(output_filename, index=False)
            logging.info(f"数据已合并保存到 {output_filename}.")

            # 删除源文件
            for file in files_to_delete:
                os.remove(file)
                logging.info(f"已删除文件：{file}")
        else:
            logging.error("没有数据可以合并.")

def load_json_and_save_to_csv(data_directory=Path(__file__).resolve().parent / 'data'):
    data_directory.mkdir(parents=True, exist_ok=True)

    # timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')

    df_lottery_info_all = []
    df_last_pool_draw_all = []
    df_list_all = []

    # Loop over all JSON files in the data directory
    for json_filename in glob.glob(str(data_directory / "lottery_page_*.json")):
        logging.info(f"Processing .json file: {json_filename}")

        # 提取页码信息
        match = re.search(r'page_(\d+)', json_filename)
        if match:
            page_number = match.group(1)
        else:
            page_number = "unknown"

        try:
            with open(json_filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                lottery_info_list = []

                # 在保存 CSV 文件时，使用 page_number 作为文件名的一部分
                last_pool_draw_csv = data_directory / f"LAST_POOL_DRAW_PAGE_{page_number}.csv"
                list_data_csv = data_directory / f"HISTORICAL_LIST_CLEANED_PAGE_{page_number}.csv"
                list_lottery_csv = data_directory / f"LOTTERY_LIST_PAGE_{page_number}.csv"

                # Process 'lastPoolDraw' data
                if "value" in data and "lastPoolDraw" in data["value"]:
                    last_pool_draw_data = data["value"]["lastPoolDraw"]
                    df_last_pool_draw = pd.DataFrame(last_pool_draw_data)
                    df_last_pool_draw.to_csv(last_pool_draw_csv, index=False)
                    df_last_pool_draw_all.append(df_last_pool_draw)
                    logging.info(f"'lastPoolDraw' data saved to CSV at {last_pool_draw_csv}.")
                else:
                    logging.error("JSON structure does not contain 'lastPoolDraw' data.")
                
                # Process 'list' data
                if "value" in data and "list" in data["value"]:
                    list_data = data["value"]["list"]
                    df_list = pd.DataFrame(list_data)
                    cleaned_df_list, cleaning_stats = clean_data(df_list)
                    if cleaned_df_list.empty:
                        logging.warning(f"No data in 'list' after cleaning for file {json_filename}.")
                    else:
                        cleaned_df_list.to_csv(list_data_csv, index=False)
                        df_list_all.append(cleaned_df_list)
                        logging.info(f"Cleaned 'list' data saved to CSV at {list_data_csv}.")
                        logging.info(f"Cleaning stats: {cleaning_stats}")
                    cleaned_df_list.to_csv(list_data_csv, index=False)
                    df_list_all.append(cleaned_df_list)
                    logging.info(f"Cleaned 'list' data saved to CSV at {list_data_csv}.")
                    logging.info(f"Cleaning stats: {cleaning_stats}")

                    for index, row in df_list.iterrows():
                        lottery_info = {
                            'lotteryDrawNum': row['lotteryDrawNum'],
                            'lotteryDrawResult': row['lotteryDrawResult'],
                            'lotteryDrawTime': row['lotteryDrawTime'],
                            'lotteryGameName': row['lotteryGameName'],
                            'totalSaleAmount': row['totalSaleAmount'],
                            'poolBalanceAfterdraw': row['poolBalanceAfterdraw']
                        }
                        lottery_info_list.append(lottery_info)
                        logging.info(f"日期: {row['lotteryDrawTime']}, 期号: {row['lotteryDrawNum']}, 开奖结果: {row['lotteryDrawResult']}, 销售额(元):{row['totalSaleAmount']}, 奖池奖金(元):{row['poolBalanceAfterdraw']}, 彩票名称: {row['lotteryGameName']}")
                        logging.info("-" * 50)
                else:
                    logging.error("JSON structure does not contain 'list' data.")
                
                df_lottery_info = pd.DataFrame(lottery_info_list)
                df_lottery_info_all.append(df_lottery_info)

                if not df_lottery_info.empty:
                    df_lottery_info.to_csv(list_lottery_csv, index=False, encoding='utf-8')
                    logging.info(f"Lottery data is save to: {list_lottery_csv}")
                else:
                    logging.error("lottery data load failed.")
                
        except Exception as e:
            logging.error(f"Error processing data: {e}")

    # Concatenate all dataframes
    df_last_pool_draw_all = pd.concat(df_last_pool_draw_all, ignore_index=True)
    df_list_all = pd.concat(df_list_all, ignore_index=True)
    df_lottery_info_all = pd.concat(df_lottery_info_all, ignore_index=True)

    patterns = ['app/data/HISTORICAL_LIST_CLEANED_PAGE_*.csv', 'app/data/LAST_POOL_DRAW_PAGE_*.csv', 'app/data/LOTTERY_LIST_PAGE_*.csv']
    output_filenames = ['app/data/combined_historical.csv', 'app/data/combined_last_pool.csv', 'app/data/combined_lottery.csv']
    concatenate_and_delete_files(patterns, output_filenames)

    return df_lottery_info_all, df_last_pool_draw_all, df_list_all
