# app/config.py
# 现有的API配置
API_URL = f'https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry'
API_PARAMS = {
    'gameNo': 85,
    'provinceId': 0,
    'pageSize': 30,
    'isVerify': 1,
    'pageNo': 1,
}

# 添加请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
ANALYSIS_DATA_FILE = 'app/data/combined_lottery.csv'