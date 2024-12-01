import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_bollinger_bands(df, window=20, num_std=2):
    """Bollinger Bands hesaplama"""
    df['MA_20'] = df['close'].rolling(window=window).mean()
    df['STD_20'] = df['close'].rolling(window=window).std()
    df['BBU_20_2'] = df['MA_20'] + (df['STD_20'] * num_std)
    df['BBL_20_2'] = df['MA_20'] - (df['STD_20'] * num_std)
    return df

def calculate_rsi(df, period=14):
    """RSI hesaplama"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_sma(df, periods=[20, 50, 200]):
    """SMA hesaplama"""
    for period in periods:
        df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
    return df

def calculate_ema(df, periods=[20, 50, 200]):
    """EMA hesaplama"""
    for period in periods:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """MACD hesaplama"""
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']
    return df

def calculate_supertrend(df, period=10, multiplier=3):
    """SuperTrend hesaplama"""
    hl2 = (df['high'] + df['low']) / 2
    atr = df['high'].sub(df['low']).rolling(period).mean()
    
    # Basic Bands
    basic_ub = hl2 + (multiplier * atr)
    basic_lb = hl2 - (multiplier * atr)
    
    # Final Bands
    df['final_ub'] = basic_ub
    df['final_lb'] = basic_lb
    
    for i in range(period, len(df)):
        if df['close'].iloc[i-1] <= df['final_ub'].iloc[i-1]:
            df['final_ub'].iloc[i] = min(basic_ub.iloc[i], df['final_ub'].iloc[i-1])
        else:
            df['final_ub'].iloc[i] = basic_ub.iloc[i]
    
        if df['close'].iloc[i-1] >= df['final_lb'].iloc[i-1]:
            df['final_lb'].iloc[i] = max(basic_lb.iloc[i], df['final_lb'].iloc[i-1])
        else:
            df['final_lb'].iloc[i] = basic_lb.iloc[i]
    
    df['SuperTrend'] = np.nan
    for i in range(period, len(df)):
        if df['close'].iloc[i] <= df['final_ub'].iloc[i]:
            df['SuperTrend'].iloc[i] = df['final_ub'].iloc[i]
        else:
            df['SuperTrend'].iloc[i] = df['final_lb'].iloc[i]
    
    return df

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

def apply_indicators(df, settings=None):
    """Tüm indikatörleri uygula"""
    try:
        # Varsayılan ayarları kullan eğer settings parametresi verilmemişse
        if settings is None:
            settings = {
                'bb_period': 20,
                'bb_std': 2,
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'supertrend_period': 10,
                'supertrend_multiplier': 3,
                'dmi_period': 14
            }

        # Tüm indikatörleri hesapla
        df = calculate_bollinger_bands(df, settings['bb_period'], settings['bb_std'])
        df = calculate_rsi(df, settings['rsi_period'])
        df = calculate_sma(df)
        df = calculate_ema(df)
        df = calculate_macd(df, settings['macd_fast'], settings['macd_slow'], settings['macd_signal'])
        df = calculate_supertrend(df, settings['supertrend_period'], settings['supertrend_multiplier'])
        df = calculate_dmi(df, settings['dmi_period'])
        
        # Gereksiz sütunları temizle
        columns_to_drop = ['TR', 'HD', 'LD', 'PDM', 'NDM', 'final_ub', 'final_lb']
        df = df.drop(columns=columns_to_drop, errors='ignore')
        
        # NaN değerleri temizle
        df.dropna(inplace=True)
        
        return df
    except Exception as e:
        logger.error(f"İndikatör hesaplama hatası: {str(e)}")
        return None
