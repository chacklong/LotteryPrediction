# app/routes/data.py
from typing import Dict
from fastapi import APIRouter, HTTPException
from ..models import fetch_all_pages, load_json_and_save_to_csv
from ..get_json import get_json_filename
from ..config import API_URL, API_PARAMS
import logging,json
import pandas as pd
from pathlib import Path
from fastapi.encoders import jsonable_encoder
from asyncio import Lock

router = APIRouter()
lock = Lock()

@router.get("/", tags=["data"])
async def get_default_message() -> Dict[str, str]:
    """
    默认路由，返回基本的欢迎消息。
    """
    try:
        logging.info("默认路由被调用")
        return {"message": "默认响应成功"}
    except Exception as e:
        logging.error(f"默认路由错误: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")
    
@router.get("/api/fetch/", tags=["fetch"])
async def fetch_lottery_data():
    """
    异步抓取彩票数据。如果锁已被占用，表示当前有正在进行的数据抓取任务。
    """
    if lock.locked():
        return {"message": "Data fetching is already in progress. Please wait until the current process finishes."}
    async with lock:
        try:
            fetch_all_pages(API_URL, API_PARAMS)
            return {"message": "Data successfully obtained and processed."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/api/conversion/", tags=["fetch"])
async def conversion_data():
    """
    将抓取的JSON数据转换为CSV格式。
    """
    load_json_and_save_to_csv()
    return {"message": "conversion data is succssfully."}
    
@router.get("/api/lastpool/", tags=["data"])
async def fetch_last_pool_draw():
    """
    从本地存储的最新JSON文件中获取最新的彩池抽取信息。
    """
    data_directory = Path(__file__).resolve().parent.parent / 'data'
    json_file_path = get_json_filename(data_directory)
    if not json_file_path:
        logging.error(f"在目录中未找到 JSON 文件: {data_directory}")
        raise HTTPException(status_code=404, detail="目录中未找到 JSON 文件")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        logging.error(f"从 {json_file_path} 解码 JSON 时出错")
        raise HTTPException(status_code=500, detail="解码 JSON 出错")
    except Exception as e:
        logging.error(f"读取 {json_file_path} 时发生错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    if "value" in data and "lastPoolDraw" in data["value"]:
        last_pool_draw_data = data["value"]["lastPoolDraw"]
        return {"message": "成功检索到 LastPoolDraw 数据", "data": last_pool_draw_data}
    else:
        logging.error(f"JSON 数据结构中不存在 'lastPoolDraw' 键。当前数据: {data}")
        raise HTTPException(status_code=404, detail="JSON 结构中不存在 'lastPoolDraw' 数据。")

@router.get("/api/listdata/", tags=["data"])
async def fetch_list_data():
    """
    从本地存储的JSON文件中获取列表数据，并将其转换为DataFrame后返回。
    """
    data_directory = Path(__file__).resolve().parent.parent / 'data'
    json_file_path = get_json_filename(data_directory)
    if not json_file_path:
        logging.error(f"在目录中未找到 JSON 文件: {data_directory}")
        raise HTTPException(status_code=404, detail="目录中未找到 JSON 文件")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        logging.error(f"读取 {json_file_path} 时发生错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    if "value" in data and "list" in data["value"]:
        list_data = data["value"]["list"]
        df_list = pd.DataFrame(list_data)
        # Directly convert DataFrame to JSON without cleaning
        result = jsonable_encoder({"message": "List data retrieved successfully",
                                   "data": df_list.to_dict(orient="records")})
        return result
    else:
        logging.error("JSON 数据中缺少 'list' 键。")
        raise HTTPException(status_code=404, detail="JSON structure does not contain 'list' data.")