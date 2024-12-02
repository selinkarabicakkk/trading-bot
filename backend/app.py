from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from fetch_data import fetch_data
from backtest_runner import BacktestRunner
from typing import List, Dict, Any
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestRequest(BaseModel):
    symbols: List[str]
    timeframes: List[str]
    indicators: List[Dict[str, Any]]

@app.post("/api/run-backtest")
async def run_backtest(request: BacktestRequest):
    """Backtest'i çalıştır"""
    try:
        logger.info(f"Backtest isteği alındı: {request.dict()}")
        
        if not request.symbols or not request.timeframes or not request.indicators:
            raise HTTPException(status_code=400, detail="Eksik parametreler")
            
        if len(request.symbols) != 1:
            raise HTTPException(status_code=400, detail="Sadece bir sembol seçilebilir")

        symbol = request.symbols[0]
        timeframe = request.timeframes[0]
        
        logger.info(f"Veri çekiliyor: {symbol} - {timeframe}")
        df = fetch_data(symbol, timeframe)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Veri bulunamadı: {symbol} - {timeframe}")
            
        logger.info("Backtest başlatılıyor...")
        runner = BacktestRunner()
        result = runner.run_backtest(df, request.indicators)
        
        if not result:
            raise HTTPException(status_code=500, detail="Backtest sonuçları hesaplanamadı")

        # Sonuçları düzenle ve döndür
        response = {
            symbol: {
                timeframe: {
                    "start_time": df.index[0].isoformat(),
                    "end_time": df.index[-1].isoformat(),
                    **result
                }
            }
        }
        
        logger.info("Backtest başarıyla tamamlandı")
        return response

    except HTTPException as he:
        logger.error(f"HTTP hatası: {he.detail}")
        raise he
    except Exception as e:
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
