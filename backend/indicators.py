import pandas as pd
import numpy as np
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def calculate_bollinger_bands(df, window=20, num_std=2):
    """Bollinger Bands hesaplama"""
    df['MA_20'] = df['close'].rolling(window=window).mean()
    df['STD_20'] = df['close'].rolling(window=window).std()
    df['BBU_20_2'] = df['MA_20'] + (df['STD_20'] * num_std)
    df['BBL_20_2'] = df['MA_20'] - (df['STD_20'] * num_std)
    return df

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

def calculate_ema(df, periods=[20, 50, 200]):
    """EMA hesaplama"""
    for period in periods:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
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

def calculate_supertrend(df, period=10, multiplier=3):
    """SuperTrend hesaplama"""
    try:
        # ATR hesaplama
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(period).mean()
        
        # Supertrend hesaplama
        hl2 = (df['high'] + df['low']) / 2
        df['final_upperband'] = hl2 + (multiplier * atr)
        df['final_lowerband'] = hl2 - (multiplier * atr)
        df['supertrend'] = df['final_upperband'].copy()
        df['supertrend_direction'] = pd.Series(index=df.index, data=-1)
        
        for i in range(period, len(df)):
            curr_close = df['close'].iloc[i]
            curr_upper = df['final_upperband'].iloc[i]
            curr_lower = df['final_lowerband'].iloc[i]
            prev_supertrend = df['supertrend'].iloc[i-1]
            
            if prev_supertrend == df['final_upperband'].iloc[i-1]:
                if curr_close > curr_upper:
                    df.loc[df.index[i], 'supertrend'] = curr_lower
                    df.loc[df.index[i], 'supertrend_direction'] = 1
                else:
                    df.loc[df.index[i], 'supertrend'] = curr_upper
                    df.loc[df.index[i], 'supertrend_direction'] = -1
            else:
                if curr_close < curr_lower:
                    df.loc[df.index[i], 'supertrend'] = curr_upper
                    df.loc[df.index[i], 'supertrend_direction'] = -1
                else:
                    df.loc[df.index[i], 'supertrend'] = curr_lower
                    df.loc[df.index[i], 'supertrend_direction'] = 1
        
        # NaN değerleri temizle
        df['supertrend'] = df['supertrend'].fillna(method='ffill')
        df['supertrend_direction'] = df['supertrend_direction'].fillna(0)
        
        logger.info(f"Supertrend hesaplandı - Period: {period}, Multiplier: {multiplier}")
        return df
        
    except Exception as e:
        logger.error(f"Supertrend hesaplama hatası: {str(e)}")
        return None

def calculate_dmi(df, period=14):
    """DMI (Directional Movement Index) hesaplama"""
    # True Range
    df['TR'] = np.maximum(
        df['high'] - df['low'],
        np.maximum(
            abs(df['high'] - df['close'].shift(1)),
            abs(df['low'] - df['close'].shift(1))
        )
    )
    
    # Directional Movement
    df['HD'] = df['high'] - df['high'].shift(1)
    df['LD'] = df['low'].shift(1) - df['low']
    
    df['PDM'] = ((df['HD'] > 0) & (df['HD'] > df['LD'])) * df['HD']
    df['NDM'] = ((df['LD'] > 0) & (df['LD'] > df['HD'])) * df['LD']
    
    # Smoothed averages
    df['ATR'] = df['TR'].rolling(window=period).mean()
    df['PDI'] = (df['PDM'].rolling(window=period).mean() / df['ATR']) * 100
    df['NDI'] = (df['NDM'].rolling(window=period).mean() / df['ATR']) * 100
    
    # ADX
    df['DX'] = abs(df['PDI'] - df['NDI']) / (df['PDI'] + df['NDI']) * 100
    df['ADX'] = df['DX'].rolling(window=period).mean()
    
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
