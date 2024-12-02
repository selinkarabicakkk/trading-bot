from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from fetch_data import fetch_data
from backtest_runner import BacktestRunner
from typing import List, Dict, Any
from pydantic import BaseModel
import pandas as pd

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

# Global değişkenler
market_data = {}

class BacktestRequest(BaseModel):
    symbols: List[str]
    timeframes: List[str]
    indicators: List[Dict[str, Any]]

@app.on_event("startup")
async def startup_event():
    """Uygulama başladığında sadece market verilerini çek"""
    try:
        logger.info("Market verileri çekiliyor...")
        symbols = ["ETHUSDT", "BTCUSDT", "AVAXUSDT", "SOLUSDT", "RENDERUSDT", "FETUSDT"]
        
        for symbol in symbols:
            data = fetch_data(symbol, "1d")  # Sadece günlük veriyi çek
            if data is not None:
                market_data[symbol] = data
                logger.info(f"{symbol} verileri güncellendi")
            
        logger.info("Market verileri başarıyla çekildi")
    except Exception as e:
        logger.error(f"Market veri çekme hatası: {str(e)}")

@app.get("/api/market-data")
async def get_market_data():
    """Market verilerini döndür"""
    if not market_data:
        raise HTTPException(status_code=404, detail="Market verisi bulunamadı")
    return market_data

@app.post("/api/run-backtest")
async def run_backtest(request: BacktestRequest):
    """Backtest'i çalıştır"""
    try:
        logger.info(f"Backtest isteği alındı: {request.dict()}")
        
        if len(request.symbols) != 1:
            error_msg = "Sadece bir sembol seçilebilir"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        symbol = request.symbols[0]
        timeframe = request.timeframes[0]
        
        logger.info(f"Veri çekiliyor: {symbol} - {timeframe}")
        df = fetch_data(symbol, timeframe)
        
        if df is None or df.empty:
            error_msg = f"Veri bulunamadı: {symbol} - {timeframe}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
            
        logger.info("Backtest başlatılıyor...")
        runner = BacktestRunner()
        result = runner.run_backtest(df, request.indicators)
        
        if not result:
            error_msg = "Backtest sonuçları alınamadı"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)

        logger.info("Backtest başarıyla tamamlandı")
        return {
            symbol: {
                timeframe: result
            }
        }

    except HTTPException as he:
        logger.error(f"HTTP hatası: {he.detail}")
        raise he
    except Exception as e:
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
