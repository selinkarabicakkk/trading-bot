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

def calculate_sma(df: pd.DataFrame, params: Dict) -> pd.DataFrame:
    """SMA hesapla"""
    try:
        period = int(params.get("period", 20))
        logger.info(f"SMA hesaplanıyor - Period: {period}")
        
        # SMA hesapla
        df['sma'] = df['close'].rolling(window=period).mean()
        
        # SMA sinyalleri
        df['sma_signal'] = 0
        
        # Fiyat SMA'yı yukarı keserse alış
        df.loc[(df['close'] > df['sma']) & (df['close'].shift(1) <= df['sma'].shift(1)), 'sma_signal'] = 1
        # Fiyat SMA'yı aşağı keserse satış
        df.loc[(df['close'] < df['sma']) & (df['close'].shift(1) >= df['sma'].shift(1)), 'sma_signal'] = -1
        
        # Son değerleri logla
        last_idx = df.index[-1]
        logger.info(f"Son SMA değerleri - SMA: {df['sma'].iloc[-1]:.2f}, Fiyat: {df['close'].iloc[-1]:.2f}")
        if df['sma_signal'].iloc[-1] != 0:
            logger.info(f"SMA Sinyal üretildi: {'AL' if df['sma_signal'].iloc[-1] == 1 else 'SAT'}")
        
        return df
        
    except Exception as e:
        logger.error(f"SMA hesaplama hatası: {str(e)}")
        raise

def calculate_ema(df, periods=[20, 50, 200]):
    """EMA hesaplama"""
    for period in periods:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df

def calculate_macd(df: pd.DataFrame, params: Dict) -> pd.DataFrame:
    """MACD hesapla"""
    try:
        fast_period = int(params.get("fast_period", 12))
        slow_period = int(params.get("slow_period", 26))
        signal_period = int(params.get("signal_period", 9))
        
        logger.info(f"MACD hesaplanıyor - Fast: {fast_period}, Slow: {slow_period}, Signal: {signal_period}")
        
        # MACD Line = 12-period EMA - 26-period EMA
        exp1 = df['close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow_period, adjust=False).mean()
        macd_line = exp1 - exp2
        
        # Signal Line = 9-period EMA of MACD Line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # MACD Histogram = MACD Line - Signal Line
        macd_hist = macd_line - signal_line
        
        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_hist'] = macd_hist
        
        # MACD sinyalleri
        df['macd_signal_line'] = 0
        
        # MACD çizgisinin sinyal çizgisini yukarı kesmesi = Alış
        buy_signal = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
        # MACD çizgisinin sinyal çizgisini aşağı kesmesi = Satış
        sell_signal = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
        
        df.loc[buy_signal, 'macd_signal_line'] = 1
        df.loc[sell_signal, 'macd_signal_line'] = -1
        
        # Son değerleri logla
        last_idx = df.index[-1]
        logger.info(f"Son MACD değerleri - Line: {macd_line[last_idx]:.2f}, Signal: {signal_line[last_idx]:.2f}, Hist: {macd_hist[last_idx]:.2f}")
        if df['macd_signal_line'].iloc[-1] != 0:
            logger.info(f"MACD Sinyal üretildi: {'AL' if df['macd_signal_line'].iloc[-1] == 1 else 'SAT'}")
        
        return df
        
    except Exception as e:
        logger.error(f"MACD hesaplama hatası: {str(e)}")
        raise

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
            df = calculate_macd(df, params)
            
        elif indicator_type == "sma":
            df = calculate_sma(df, params)
        else:
            logger.warning(f"Desteklenmeyen indikatör tipi: {indicator_type}")

        return df

    except Exception as e:
        logger.error(f"İndikatör uygulama hatası: {str(e)}")
        return df
