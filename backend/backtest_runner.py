from fetch_data import fetch_data
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class BacktestRunner:
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = None
        self.trades = []
        self.trade_history = []

    def calculate_indicators(self, df: pd.DataFrame, indicators: List[Dict[str, Any]]) -> pd.DataFrame:
        for indicator in indicators:
            if indicator["type"] == "rsi":
                period = indicator["params"]["period"]
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                df['rsi'] = 100 - (100 / (1 + rs))
                
            elif indicator["type"] == "macd":
                fast = indicator["params"]["fastPeriod"]
                slow = indicator["params"]["slowPeriod"]
                signal = indicator["params"]["signalPeriod"]
                
                exp1 = df['close'].ewm(span=fast, adjust=False).mean()
                exp2 = df['close'].ewm(span=slow, adjust=False).mean()
                df['macd'] = exp1 - exp2
                df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
                
            elif indicator["type"] == "bollinger":
                period = indicator["params"]["period"]
                std_dev = indicator["params"]["stdDev"]
                
                df['bb_middle'] = df['close'].rolling(window=period).mean()
                df['bb_upper'] = df['bb_middle'] + (df['close'].rolling(window=period).std() * std_dev)
                df['bb_lower'] = df['bb_middle'] - (df['close'].rolling(window=period).std() * std_dev)
                
            elif indicator["type"] in ["sma", "ema"]:
                period = indicator["params"]["period"]
                if indicator["type"] == "sma":
                    df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
                else:
                    df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

        return df

    def generate_signals(self, df: pd.DataFrame, indicators: List[Dict[str, Any]]) -> pd.Series:
        signals = pd.Series(index=df.index, data=0)
        
        for indicator in indicators:
            if indicator["type"] == "rsi":
                # RSI sinyalleri
                signals = signals.where(
                    ~((df['rsi'] < indicator["params"]["oversold"]) & (signals == 0)), 1)
                signals = signals.where(
                    ~((df['rsi'] > indicator["params"]["overbought"]) & (signals == 1)), -1)
                
            elif indicator["type"] == "macd":
                # MACD sinyalleri
                signals = signals.where(
                    ~((df['macd'] > df['signal']) & (df['macd'].shift(1) <= df['signal'].shift(1))), 1)
                signals = signals.where(
                    ~((df['macd'] < df['signal']) & (df['macd'].shift(1) >= df['signal'].shift(1))), -1)
                
            elif indicator["type"] == "bollinger":
                # Bollinger Bands sinyalleri
                signals = signals.where(~(df['close'] < df['bb_lower']), 1)
                signals = signals.where(~(df['close'] > df['bb_upper']), -1)
            
            elif indicator["type"] == "sma":
                period = indicator["params"]["period"]
                signals = signals.where(
                    ~((df['close'] > df[f'sma_{period}']) & (df['close'].shift(1) <= df[f'sma_{period}'].shift(1))), 1)
                signals = signals.where(
                    ~((df['close'] < df[f'sma_{period}']) & (df['close'].shift(1) >= df[f'sma_{period}'].shift(1))), -1)
            
            elif indicator["type"] == "ema":
                period = indicator["params"]["period"]
                signals = signals.where(
                    ~((df['close'] > df[f'ema_{period}']) & (df['close'].shift(1) <= df[f'ema_{period}'].shift(1))), 1)
                signals = signals.where(
                    ~((df['close'] < df[f'ema_{period}']) & (df['close'].shift(1) >= df[f'ema_{period}'].shift(1))), -1)

        # Sinyal filtreleme
        signals = signals.fillna(0)
        return signals

    def run_backtest(self, symbol: str, timeframe: str, indicators: List[Dict[str, Any]]) -> Dict:
        try:
            # Veri çekme
            df = fetch_data(symbol, timeframe)
            if df.empty:
                return None

            # DataFrame'i temizle ve sayısal değerlere dönüştür
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df = df.dropna(subset=['close'])  # NaN değerleri olan satırları kaldır

            if len(df) < 2:  # En az 2 veri noktası gerekli
                return None

            # İndikatörleri hesapla
            df = self.calculate_indicators(df, indicators)
            
            # Sinyalleri oluştur
            signals = self.generate_signals(df, indicators)
            
            # Backtest başlangıcı
            self.balance = float(self.initial_balance)
            self.position = None
            self.trades = []
            current_position = None
            total_volume = 0.0
            
            # Fiyat bilgilerini baştan hesapla
            start_price = float(df['close'].iloc[0])
            end_price = float(df['close'].iloc[-1])
            price_change = end_price - start_price
            price_change_percentage = (price_change / start_price) * 100 if start_price > 0 else 0.0
            
            for i in range(len(df)):
                try:
                    current_price = float(df['close'].iloc[i])
                    signal = float(signals.iloc[i])
                    
                    if signal == 1 and current_position is None:  # Alış sinyali
                        position_size = self.balance * 0.95  # %95'ini kullan
                        amount = position_size / current_price if current_price > 0 else 0
                        
                        if amount > 0:
                            current_position = {
                                'amount': amount,
                                'entry_price': current_price,
                                'entry_time': df.index[i]
                            }
                            self.balance -= position_size
                            total_volume += position_size
                        
                    elif signal == -1 and current_position is not None:  # Satış sinyali
                        exit_value = current_position['amount'] * current_price
                        profit = exit_value - (current_position['amount'] * current_position['entry_price'])
                        self.balance += exit_value
                        total_volume += exit_value
                        
                        self.trades.append({
                            'entry_time': current_position['entry_time'],
                            'exit_time': df.index[i],
                            'entry_price': current_position['entry_price'],
                            'exit_price': current_price,
                            'amount': current_position['amount'],
                            'profit': profit,
                            'profit_percentage': (profit / (current_position['amount'] * current_position['entry_price'])) * 100
                        })
                        current_position = None
                except Exception as e:
                    logger.error(f"İşlem hatası: {str(e)}")
                    continue

            # Son pozisyonu kapat
            if current_position is not None:
                try:
                    exit_value = current_position['amount'] * end_price
                    profit = exit_value - (current_position['amount'] * current_position['entry_price'])
                    self.balance += exit_value
                    total_volume += exit_value
                    
                    self.trades.append({
                        'entry_time': current_position['entry_time'],
                        'exit_time': df.index[-1],
                        'entry_price': current_position['entry_price'],
                        'exit_price': end_price,
                        'amount': current_position['amount'],
                        'profit': profit,
                        'profit_percentage': (profit / (current_position['amount'] * current_position['entry_price'])) * 100
                    })
                except Exception as e:
                    logger.error(f"Son pozisyon kapatma hatası: {str(e)}")

            # Sonuçları hesapla
            total_trades = len(self.trades)
            winning_trades = len([t for t in self.trades if t['profit'] > 0])
            total_profit = sum(t['profit'] for t in self.trades) if self.trades else 0.0
            
            # Drawdown hesaplama
            cumulative_returns = [0.0]
            peak = float(self.initial_balance)
            drawdowns = []
            
            for trade in self.trades:
                try:
                    cumulative_returns.append(cumulative_returns[-1] + trade['profit'])
                    current_balance = self.initial_balance + cumulative_returns[-1]
                    peak = max(peak, current_balance)
                    drawdown = (peak - current_balance) / peak * 100 if peak > 0 else 0.0
                    drawdowns.append(drawdown)
                except Exception as e:
                    logger.error(f"Drawdown hesaplama hatası: {str(e)}")
                    continue
            
            max_drawdown = max(drawdowns) if drawdowns else 0.0
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
            profit_percentage = (total_profit / self.initial_balance * 100) if self.initial_balance > 0 else 0.0

            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'initial_balance': round(float(self.initial_balance), 2),
                'final_balance': round(float(self.balance), 2),
                'total_profit': round(float(total_profit), 2),
                'total_profit_percentage': round(float(profit_percentage), 2),
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': round(float(win_rate), 2),
                'max_drawdown': round(float(max_drawdown), 2),
                'total_volume': round(float(total_volume), 2),
                'start_price': round(float(start_price), 2),
                'end_price': round(float(end_price), 2),
                'price_change_percentage': round(float(price_change_percentage), 2),
                'indicators_used': [ind['type'] for ind in indicators]
            }

        except Exception as e:
            logger.error(f"Backtest hatası: {str(e)}")
            return None

def run_backtest_analysis(symbol: str, timeframe: str, indicators: List[Dict[str, Any]] = None) -> Dict:
    if indicators is None:
        indicators = [
            {
                "type": "rsi",
                "params": {"period": 14, "overbought": 70, "oversold": 30}
            },
            {
                "type": "macd",
                "params": {"fastPeriod": 12, "slowPeriod": 26, "signalPeriod": 9}
            }
        ]
    
    runner = BacktestRunner()
    return runner.run_backtest(symbol, timeframe, indicators)