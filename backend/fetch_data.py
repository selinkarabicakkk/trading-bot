from config import client
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mainnet'den veri çekme fonksiyonu
def fetch_data(symbol, interval="1h", limit=100):
    try:
        logger.info(f"Veri çekme başladı: {symbol} - {interval}")
        
        # Mainnet'den veri çek
        klines = client.get_klines(
            symbol=symbol.upper(),
            interval=interval,
            limit=limit
        )
        
        if not klines:
            logger.warning("Binance'den veri alınamadı")
            return pd.DataFrame()
            
        logger.info(f"Binance'den {len(klines)} adet veri alındı")
        
        # DataFrame oluştur
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        # Veri tiplerini düzenle
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["open"] = pd.to_numeric(df["open"])
        df["high"] = pd.to_numeric(df["high"])
        df["low"] = pd.to_numeric(df["low"])
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        
        # Sadece gerekli kolonları döndür
        return df[["timestamp", "open", "high", "low", "close", "volume"]]
    except Exception as e:
        logger.error(f"Veri çekme hatası: {str(e)}")
        raise Exception(f"Veri çekme hatası: {str(e)}")

# Desteklenen sembolleri listelemek için bir fonksiyon
def get_valid_symbols():
    info = client.get_exchange_info()
    return [s["symbol"] for s in info["symbols"]]
