import pandas as pd
import numpy as np
import logging
from typing import Dict

logger = logging.getLogger(__name__)



def calculate_rsi(df: pd.DataFrame, period: int = 14, overbought: int = 70, oversold: int = 30) -> pd.DataFrame:
    """RSI hesaplama"""
    try:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # RSI sinyalleri
        df['rsi_signal'] = 0
        df.loc[df['RSI'] < oversold, 'rsi_signal'] = 1  # Aşırı satım - Alış sinyali
        df.loc[df['RSI'] > overbought, 'rsi_signal'] = -1  # Aşırı alım - Satış sinyali
        
        logger.info(f"RSI hesaplandı - Period: {period}, Overbought: {overbought}, Oversold: {oversold}")
        return df
    except Exception as e:
        logger.error(f"RSI hesaplama hatası: {str(e)}")
        return df

def calculate_sma(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """SMA hesaplama"""
    try:
        df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
        
        # SMA sinyalleri
        df['sma_signal'] = 0
        df.loc[df['close'] > df[f'SMA_{period}'], 'sma_signal'] = 1  # Fiyat SMA üzerinde - Alış sinyali
        df.loc[df['close'] < df[f'SMA_{period}'], 'sma_signal'] = -1  # Fiyat SMA altında - Satış sinyali
        
        logger.info(f"SMA hesaplandı - Period: {period}")
        return df
    except Exception as e:
        logger.error(f"SMA hesaplama hatası: {str(e)}")
        return df


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """MACD hesaplama"""
    try:
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # MACD sinyalleri
        df['macd_signal'] = 0
        # MACD çizgisi sinyal çizgisini yukarı keserse alış
        df.loc[(df['MACD'] > df['Signal']) & (df['MACD'].shift(1) <= df['Signal'].shift(1)), 'macd_signal'] = 1
        # MACD çizgisi sinyal çizgisini aşağı keserse satış
        df.loc[(df['MACD'] < df['Signal']) & (df['MACD'].shift(1) >= df['Signal'].shift(1)), 'macd_signal'] = -1
        
        logger.info(f"MACD hesaplandı - Fast: {fast}, Slow: {slow}, Signal: {signal}")
        return df
    except Exception as e:
        logger.error(f"MACD hesaplama hatası: {str(e)}")
        return df

def apply_indicators(df: pd.DataFrame, indicator_type: str, params: Dict = None) -> pd.DataFrame:
    """Seçilen indikatörü uygula"""
    try:
        if indicator_type is None:
            logger.error("İndikatör tipi belirtilmedi")
            return df

        if df is None or df.empty:
            logger.error("Veri çerçevesi boş")
            return df

        indicator_type = indicator_type.lower().strip()
        logger.info(f"İndikatör uygulanıyor: {indicator_type}, parametreler: {params}")

        if params is None:
            params = {}

        if indicator_type == "rsi":
            period = params.get("period", 14)
            overbought = params.get("overbought", 70)
            oversold = params.get("oversold", 30)
            df = calculate_rsi(df, period, overbought, oversold)
            
        elif indicator_type == "macd":
            fast_period = params.get("fast_period", 12)
            slow_period = params.get("slow_period", 26)
            signal_period = params.get("signal_period", 9)
            df = calculate_macd(df, fast_period, slow_period, signal_period)
            
        elif indicator_type == "sma":
            period = params.get("period", 20)
            df = calculate_sma(df, period)
        else:
            logger.warning(f"Desteklenmeyen indikatör tipi: {indicator_type}")

        return df

    except Exception as e:
        logger.error(f"İndikatör uygulama hatası: {str(e)}")
        return df
