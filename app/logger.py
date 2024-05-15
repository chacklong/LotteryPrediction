import logging
from pathlib import Path
from logging.config import dictConfig
import json

def setup_logging():
    log_file_path = Path(__file__).parent.parent / 'logs/default.log'
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

      # 使用字典配置日志
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': log_file_path,
                'formatter': 'default',
                'encoding': 'utf-8'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'INFO'
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': True
            }
        }
    })
