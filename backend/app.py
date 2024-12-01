from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from fetch_data import fetch_data
from backtest_runner import run_backtest_analysis
from typing import List, Dict, Any
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger(__name__)

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
    """Backtest'i manuel olarak başlat"""
    try:
        all_results = []

        for symbol in request.symbols:
            for timeframe in request.timeframes:
                result = run_backtest_analysis(
                    symbol=symbol,
                    timeframe=timeframe,
                    indicators=request.indicators
                )
                if result:
                    all_results.append(result)

        if not all_results:
            logger.warning("Backtest sonuçları boş")
            return []

        # Sonuçları düzenle
        organized_results = {}
        for result in all_results:
            symbol = result['symbol']
            timeframe = result['timeframe']
            
            if symbol not in organized_results:
                organized_results[symbol] = {}
                
            organized_results[symbol][timeframe] = {
                'initial_balance': result['initial_balance'],
                'final_balance': result['final_balance'],
                'total_profit': result['total_profit'],
                'total_profit_percentage': result['total_profit_percentage'],
                'total_trades': result['total_trades'],
                'winning_trades': result['winning_trades'],
                'win_rate': result['win_rate'],
                'max_drawdown': result['max_drawdown'],
                'indicators_used': result['indicators_used']
            }

        return organized_results

    except Exception as e:
        logger.error(f"Backtest API hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
