from config import client
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def convert_interval(interval: str) -> str:
    """Interval dönüşümü"""
    interval_map = {
        "1": "1m",
        "15": "15m",
        "60": "1h",
        "240": "4h",
        "D": "1d",
        "1d": "1d",  # Doğrudan gelen günlük interval için
        "1h": "1h",  # Doğrudan gelen saatlik interval için
        "15m": "15m",  # Doğrudan gelen 15 dakikalık interval için
        "4h": "4h",   # Doğrudan gelen 4 saatlik interval için
        "1m": "1m"    # Doğrudan gelen 1 dakikalık interval için
    }
    mapped_interval = interval_map.get(interval)
    if not mapped_interval:
        logger.warning(f"Bilinmeyen interval: {interval}, varsayılan olarak 1m kullanılıyor")
        return "1m"  # Varsayılan olarak 1 dakika
    return mapped_interval

def calculate_limit_for_4_months(interval: str) -> int:
    """4 aylık veri için gereken limit değerini hesapla"""
    # 4 ay = 120 gün
    minutes_in_4_months = 120 * 24 * 60  # 120 gün * 24 saat * 60 dakika
    
    interval_minutes = {
        "1m": 1,     # 1 dakika
        "15m": 15,   # 15 dakika
        "1h": 60,    # 1 saat
        "4h": 240,   # 4 saat
        "1d": 1440   # 1 gün
    }
    
    minutes = interval_minutes.get(interval, 1)  # Varsayılan olarak 1 dakika
    limit = min(minutes_in_4_months // minutes, 1000)  # Binance limiti 1000
    
    logger.info(f"4 aylık veri için {interval} interval'ında {limit} mum gerekiyor")
    return limit

def fetch_data(symbol: str, interval: str = "1d", limit: int = None) -> Optional[pd.DataFrame]:
    """Binance'den veri çek"""
    try:
        logger.info(f"Veri çekme başladı: {symbol} - {interval}")
        
        # Interval dönüşümü
        binance_interval = convert_interval(interval)
        logger.info(f"Dönüştürülen interval: {binance_interval}")
        
        # Limit belirtilmemişse 4 aylık veri için hesapla
        if limit is None:
            limit = calculate_limit_for_4_months(binance_interval)
        
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
