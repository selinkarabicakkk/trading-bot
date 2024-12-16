from fetch_data import fetch_data
from indicators import calculate_rsi, calculate_macd, calculate_sma, apply_indicators
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
        """İndikatörleri hesapla"""
        try:
            logger.info(f"İndikatör hesaplaması başlıyor... İndikatör sayısı: {len(indicators)}")
            
            for indicator in indicators:
                indicator_type = indicator.get("type", "").lower().strip()
                params = indicator.get("params", {})
                logger.info(f"İndikatör hesaplanıyor: {indicator_type}, Parametreler: {params}")
                
                df = apply_indicators(df, indicator_type, params)
                if df is None:
                    raise ValueError(f"İndikatör hesaplama başarısız: {indicator_type}")
            
            return df
            
        except Exception as e:
            logger.error(f"İndikatör hesaplama hatası: {str(e)}")
            raise

    def generate_signals(self, df: pd.DataFrame, indicators: List[Dict]) -> pd.Series:
        """İndikatörlere göre alım/satım sinyalleri üret"""
        try:
            logger.info("Sinyal üretimi başlıyor... İndikatör sayısı: %d", len(indicators))
            logger.info("Aktif indikatörler: %s", [ind["type"] for ind in indicators])
            
            if len(indicators) == 1:
                logger.info("Tek indikatör modu")
                indicator = indicators[0]
                ind_type = indicator["type"].lower()
                
                if ind_type == "macd":
                    # MACD sinyalleri
                    macd = df['macd']
                    signal = df['macd_signal']
                    hist = df['macd_hist']
                    
                    # Sinyal üretimi
                    signals = pd.Series(0, index=df.index)
                    
                    # MACD çizgisinin sinyal çizgisini yukarı kesmesi = Alış
                    buy_signal = (macd > signal) & (macd.shift(1) <= signal.shift(1))
                    # MACD çizgisinin sinyal çizgisini aşağı kesmesi = Satış
                    sell_signal = (macd < signal) & (macd.shift(1) >= signal.shift(1))
                    
                    signals[buy_signal] = 1
                    signals[sell_signal] = -1
                    
                    # Son değerleri logla
                    last_idx = df.index[-1]
                    logger.info(f"Son MACD değerleri - MACD: {macd[last_idx]:.2f}, Signal: {signal[last_idx]:.2f}, Hist: {hist[last_idx]:.2f}")
                    if signals[last_idx] != 0:
                        logger.info(f"Sinyal üretildi: {'AL' if signals[last_idx] == 1 else 'SAT'}")
                    
                    return signals
                    
                elif ind_type == "rsi":
                    # RSI sinyalleri
                    rsi = df['rsi']
                    signals = pd.Series(0, index=df.index)
                    
                    # Aşırı satım bölgesinden çıkış = Alış
                    buy_signal = (rsi > 30) & (rsi.shift(1) <= 30)
                    # Aşırı alım bölgesinden çıkış = Satış
                    sell_signal = (rsi < 70) & (rsi.shift(1) >= 70)
                    
                    signals[buy_signal] = 1
                    signals[sell_signal] = -1
                    return signals
                    
                elif ind_type == "bollinger":
                    # Bollinger sinyalleri
                    close = df['close']
                    upper = df['bb_upper']
                    lower = df['bb_lower']
                    signals = pd.Series(0, index=df.index)
                    
                    # Alt bandın altından dönüş = Alış
                    buy_signal = (close > lower) & (close.shift(1) <= lower.shift(1))
                    # Üst bandın üstünden dönüş = Satış
                    sell_signal = (close < upper) & (close.shift(1) >= upper.shift(1))
                    
                    signals[buy_signal] = 1
                    signals[sell_signal] = -1
                    return signals
                    
                elif ind_type == "sma":
                    # SMA sinyalleri
                    close = df['close']
                    sma = df['sma']
                    signals = pd.Series(0, index=df.index)
                    
                    # Fiyat SMA'yı yukarı kesiyor = Alış
                    buy_signal = (close > sma) & (close.shift(1) <= sma.shift(1))
                    # Fiyat SMA'yı aşağı kesiyor = Satış
                    sell_signal = (close < sma) & (close.shift(1) >= sma.shift(1))
                    
                    signals[buy_signal] = 1
                    signals[sell_signal] = -1
                    return signals
            
            # Birden fazla indikatör için çoğunluk kararı
            all_signals = []
            for indicator in indicators:
                ind_type = indicator["type"].lower()
                signal_col = f"{ind_type}_signal"
                if signal_col in df.columns:
                    all_signals.append(df[signal_col])
            
            if all_signals:
                # Tüm sinyallerin ortalamasını al
                combined_signals = pd.concat(all_signals, axis=1).mean(axis=1)
                # -0.5'ten küçük = Satış, 0.5'ten büyük = Alış
                return pd.Series(np.where(combined_signals > 0.5, 1, np.where(combined_signals < -0.5, -1, 0)), index=df.index)
                
            return pd.Series(0, index=df.index)
            
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {str(e)}")
            return pd.Series(0, index=df.index)

    def run_backtest(self, df: pd.DataFrame, indicators: List[Dict[str, Any]]) -> Dict:
        """Backtest işlemini çalıştır"""
        try:
            logger.info("Backtest başlıyor...")
            
            # İndikatörleri hesapla
            df = self.calculate_indicators(df, indicators)
            if df is None or df.empty:
                raise ValueError("İndikatör hesaplama başarısız")
            
            # Sinyalleri üret
            signals = self.generate_signals(df, indicators)
            
            # Alım-satım işlemleri
            trades = []
            position = None
            balance = self.initial_balance
            total_profit = 0
            
            for i in range(len(df)):
                current_price = df['close'].iloc[i]
                current_time = df.index[i]
                
                if signals.iloc[i] == 1 and position is None:  # Alış sinyali
                    position = {
                        "type": "BUY",
                        "price": current_price,
                        "timestamp": current_time.isoformat(),
                        "balance": balance
                    }
                    trades.append(position)
                    logger.info(f"Alış sinyali: {current_time}, Fiyat: {current_price}")
                    
                elif signals.iloc[i] == -1 and position is not None:  # Satış sinyali
                    # Kar/zarar hesapla
                    profit_percentage = (current_price - position["price"]) / position["price"] * 100
                    trade_profit = balance * (profit_percentage / 100)
                    balance += trade_profit
                    total_profit += trade_profit
                    
                    trade = {
                        "type": "SELL",
                        "price": current_price,
                        "timestamp": current_time.isoformat(),
                        "profit_percentage": profit_percentage,
                        "trade_profit": trade_profit,
                        "balance": balance
                    }
                    trades.append(trade)
                    position = None
                    logger.info(f"Satış sinyali: {current_time}, Fiyat: {current_price}, Kar: {profit_percentage:.2f}%, İşlem Karı: {trade_profit:.2f}, Yeni Bakiye: {balance:.2f}")
            
            # Sonuçları hesapla
            total_trades = len([t for t in trades if t["type"] == "SELL"])
            winning_trades = len([t for t in trades if t["type"] == "SELL" and t.get("trade_profit", 0) > 0])
            
            # Maksimum drawdown hesapla
            rolling_max = df['close'].expanding().max()
            drawdown = ((df['close'] - rolling_max) / rolling_max) * 100
            max_drawdown = abs(drawdown.min())
            
            # Strateji performansı yüzdesini hesapla
            strategy_performance = ((balance - self.initial_balance) / self.initial_balance) * 100
            
            result = {
                "start_price": float(df['close'].iloc[0]),
                "end_price": float(df['close'].iloc[-1]),
                "price_change_percentage": float(((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100),
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                "max_drawdown": float(max_drawdown),
                "total_profit": float(total_profit),
                "final_balance": float(balance),
                "strategy_performance": float(strategy_performance),
                "indicators_used": [ind["type"].upper() for ind in indicators],
                "trades": trades
            }
            
            logger.info(f"Backtest tamamlandı - Toplam işlem: {total_trades}, "
                       f"Kazanan işlem: {winning_trades}, "
                       f"Toplam kar: {total_profit:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest hatası: {str(e)}")
            raise