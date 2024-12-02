from config import client
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def convert_interval(interval: str) -> str:
    """Interval dönüşümü"""
    interval_map = {
        "1": "1m",
        "5": "5m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "240": "4h",
        "D": "1d",
        "W": "1w",
        "M": "1M"
    }
    mapped_interval = interval_map.get(interval)
    if not mapped_interval:
        logger.warning(f"Bilinmeyen interval: {interval}, varsayılan olarak 1d kullanılıyor")
        return "1d"
    return mapped_interval

def fetch_data(symbol: str, interval: str = "1d", limit: int = 1000) -> Optional[pd.DataFrame]:
    """Binance'den veri çek"""
    try:
        logger.info(f"Veri çekme başladı: {symbol} - {interval}")
        
        # Interval dönüşümü
        binance_interval = convert_interval(interval)
        logger.info(f"Dönüştürülen interval: {binance_interval}")
        
        # Mainnet'den veri çek
        klines = client.get_klines(
            symbol=symbol.upper(),
            interval=binance_interval,
            limit=limit
        )
        
        if not klines:
            logger.warning(f"Veri alınamadı: {symbol} - {binance_interval}")
            return None
            
        logger.info(f"Binance'den {len(klines)} adet veri alındı")
        
        # DataFrame oluştur
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        # Veri tiplerini düzenle
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN değerleri temizle
        df = df.dropna(subset=numeric_columns)
        
        if df.empty:
            logger.warning("Veri temizleme sonrası DataFrame boş")
            return None
            
        # Sadece gerekli kolonları döndür
        result_df = df[["open", "high", "low", "close", "volume"]]
        logger.info(f"İşlenmiş veri boyutu: {len(result_df)}")
        
        return result_df
        
    except Exception as e:
        logger.error(f"Veri çekme hatası: {str(e)}")
        return None

# Desteklenen sembolleri listelemek için bir fonksiyon
def get_valid_symbols():
    info = client.get_exchange_info()
    return [s["symbol"] for s in info["symbols"]]
