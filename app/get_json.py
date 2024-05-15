# app/get_json.py
from pathlib import Path
import logging

def get_json_filename(directory_path):
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        logging.error(f"指定的路径不存在或不是一个目录: {directory_path}")
        return None
    
    json_files = list(path.glob('*.json'))
    if json_files:
        return json_files[0]  # 返回第一个找到的 JSON 文件
    else:
        logging.info(f"在目录 {directory_path} 下没有找到 .json 文件")
        return None