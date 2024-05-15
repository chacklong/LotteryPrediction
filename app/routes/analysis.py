# app/routes/analysis.py
from fastapi import APIRouter, HTTPException
from ..analysis.eda import get_frequency_and_probability, time_trend_analysis, hot_and_cold_numbers, load_data
import logging

router = APIRouter()

@router.get("/api/analysis/frequency&probability/", tags=["analysis"])
async def analysis_results():
    """
    获取数字出现的频率和概率分析结果。
    """
    try:
        frequency, probability = get_frequency_and_probability()
        logging.info("Frequency: %s", frequency)
        logging.info("Probability: %s", probability)
        return {"frequency": frequency, "probability": probability}
    except Exception as e:
        logging.error(f"Failed to calculate frequency and probability: {e}")
        raise HTTPException(status_code=500, detail="Error processing the data")
    
@router.get("/api/analysis/time_trend/", tags=["analysis"])
async def time_trend():
    """
    进行时间趋势分析，查看不同时间（如每年、每月）的数字出现频率。
    """
    try:
        data = load_data()
        results = time_trend_analysis(data)
        logging.info("Time trend analysis completed successfully.")
        return results
    except Exception as e:
        logging.error(f"Failed to perform time trend analysis: {e}")
        raise HTTPException(status_code=500, detail="Error processing the data")

@router.get("/api/analysis/hot_cold_numbers/", tags=["analysis"])
async def hot_cold():
    """
    识别出现频率最高的热号和频率最低的冷号。
    """
    try:
        data = load_data()
        results = hot_and_cold_numbers(data)
        logging.info("Hot and Cold numbers identified successfully.")
        return results
    except Exception as e:
        logging.error(f"Failed to identify hot and cold numbers: {e}")
        raise HTTPException(status_code=500, detail="Error processing the data")