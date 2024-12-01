from indicators import apply_indicators
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BacktestStrategy:
    def __init__(self, df, symbol, timeframe):
        """
        Args:
            df (pd.DataFrame): İşlenecek veri
            symbol (str): Coin sembolü
            timeframe (str): Zaman dilimi
        """
        self.df = df.copy()
        self.symbol = symbol
        self.timeframe = timeframe
        self.results = []

    def run(self):
        try:
            # İndikatörleri hesapla
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
            
            self.df = apply_indicators(self.df, settings)
            if self.df is None:
                logger.error(f"İndikatör hesaplama başarısız: {self.symbol} - {self.timeframe}")
                return None
            
            # Strateji sinyallerini hesapla
            self.calculate_signals()
            
            # Sonuçları hesapla
            return self.calculate_results()
            
        except Exception as e:
            logger.error(f"Backtest hatası ({self.symbol} - {self.timeframe}): {str(e)}")
            return None
    
    def calculate_signals(self):
        """Alım-satım sinyallerini hesapla"""
        try:
            df = self.df
            
            # RSI koşulları
            df['buy_signal_rsi'] = (df['RSI'] < 30)
            df['sell_signal_rsi'] = (df['RSI'] > 70)
            
            # Bollinger Bands koşulları
            df['buy_signal_bb'] = (df['close'] < df['BBL_20_2'])
            df['sell_signal_bb'] = (df['close'] > df['BBU_20_2'])
            
            # MACD koşulları
            df['buy_signal_macd'] = (df['MACD'] > df['Signal'])
            df['sell_signal_macd'] = (df['MACD'] < df['Signal'])
            
            # SuperTrend koşulları
            df['buy_signal_st'] = (df['close'] > df['SuperTrend'])
            df['sell_signal_st'] = (df['close'] < df['SuperTrend'])
            
            # DMI koşulları
            df['buy_signal_dmi'] = (df['PDI'] > df['NDI']) & (df['ADX'] > 25)
            df['sell_signal_dmi'] = (df['PDI'] < df['NDI']) & (df['ADX'] > 25)
            
            # Tüm sinyalleri birleştir
            df['buy_signal'] = (
                df['buy_signal_rsi'] & 
                df['buy_signal_bb'] & 
                df['buy_signal_macd'] & 
                df['buy_signal_st'] & 
                df['buy_signal_dmi']
            )
            
            df['sell_signal'] = (
                df['sell_signal_rsi'] & 
                df['sell_signal_bb'] & 
                df['sell_signal_macd'] & 
                df['sell_signal_st'] & 
                df['sell_signal_dmi']
            )
            
        except Exception as e:
            logger.error(f"Sinyal hesaplama hatası: {str(e)}")
    
    def calculate_results(self):
        """Backtest sonuçlarını hesapla"""
        try:
            df = self.df
            position = 0
            entry_price = 0
            trades = []
            
            for i in range(1, len(df)):
                if position == 0 and df['buy_signal'].iloc[i]:
                    position = 1
                    entry_price = df['close'].iloc[i]
                    trades.append({
                        'type': 'buy',
                        'price': entry_price,
                        'time': df.index[i]
                    })
                elif position == 1 and df['sell_signal'].iloc[i]:
                    position = 0
                    exit_price = df['close'].iloc[i]
                    profit = ((exit_price - entry_price) / entry_price) * 100
                    trades.append({
                        'type': 'sell',
                        'price': exit_price,
                        'time': df.index[i],
                        'profit': profit
                    })
            
            if not trades:
                return None
            
            # Sonuçları hesapla
            total_trades = len([t for t in trades if t['type'] == 'sell'])
            if total_trades == 0:
                return None
                
            winning_trades = len([t for t in trades if t['type'] == 'sell' and t['profit'] > 0])
            total_profit = sum([t['profit'] for t in trades if t['type'] == 'sell'])
            
            return {
                'symbol': self.symbol,
                'timeframe': self.timeframe,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': (winning_trades / total_trades) * 100 if total_trades > 0 else 0,
                'total_profit': total_profit,
                'avg_profit': total_profit / total_trades if total_trades > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Sonuç hesaplama hatası: {str(e)}")
            return None