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

    def generate_signals(self, df: pd.DataFrame, indicators: List[Dict[str, Any]]) -> pd.Series:
        """Her indikatör için sinyal üret ve kombine et"""
        try:
            logger.info(f"Sinyal üretimi başlıyor... İndikatör sayısı: {len(indicators)}")
            
            # Her indikatör için sinyal kolonlarını topla
            indicator_signals = []
            active_indicators = []
            
            for indicator in indicators:
                indicator_type = indicator.get("type", "").lower().strip()
                signal_column = f"{indicator_type}_signal"
                
                if signal_column in df.columns:
                    indicator_signals.append(df[signal_column])
                    active_indicators.append(indicator_type)
                else:
                    logger.warning(f"Sinyal kolonu bulunamadı: {signal_column}")
            
            logger.info(f"Aktif indikatörler: {active_indicators}")
            
            if not indicator_signals:
                logger.error("Hiç sinyal bulunamadı")
                raise ValueError("Sinyal üretilemedi")
            
            # Sinyal kombinasyonlarını hesapla
            signal_sum = sum(indicator_signals)
            combined_signal = pd.Series(0, index=df.index)
            
            # Tek indikatör varsa direkt onun sinyallerini kullan
            if len(indicator_signals) == 1:
                logger.info("Tek indikatör modu")
                combined_signal = indicator_signals[0]
            else:
                # Birden fazla indikatör için çoğunluk oylaması
                threshold = len(indicator_signals) // 2
                combined_signal[signal_sum > threshold] = 1  # Çoğunluk alış diyorsa
                combined_signal[signal_sum < -threshold] = -1  # Çoğunluk satış diyorsa
            
            signal_counts = {
                "buy": len(combined_signal[combined_signal == 1]),
                "sell": len(combined_signal[combined_signal == -1])
            }
            logger.info(f"Sinyal sayıları: {signal_counts}")
            
            return combined_signal
            
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {str(e)}")
            raise

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