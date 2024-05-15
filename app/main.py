# app/main.py
from fastapi import FastAPI
from .routes import data, analysis
from .logger import setup_logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 同源策略配置
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",  
    "http://192.168.136.171:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

setup_logging()
app.include_router(data.router)
app.include_router(analysis.router)