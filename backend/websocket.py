from fastapi import WebSocket
import json
import asyncio
from binance import AsyncClient, BinanceSocketManager
import logging
import pandas as pd
import certifi
import ssl
import os
from config import api_key, api_secret

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceWebsocketManager:
    def __init__(self):
        self.active_connections = []
        self.tasks = {}
        self.socket_manager = None
        self.client = None
        self.indicator_settings = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Yeni WebSocket bağlantısı kabul edildi")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        symbol = next((s for s, ws in self.tasks.items() if ws == websocket), None)
        if symbol and symbol in self.tasks:
            self.tasks[symbol].cancel()
            del self.tasks[symbol]
        logger.info("WebSocket bağlantısı kapatıldı")

    async def initialize_socket(self):
        if not self.client:
            self.client = await AsyncClient.create(
                api_key=api_key,
                api_secret=api_secret,
                tld='com',
                requests_params={
                    'verify': False,
                    'timeout': 30
                }
            )
            self.socket_manager = BinanceSocketManager(self.client)
            logger.info("Binance AsyncClient başlatıldı")

    async def handle_socket_message(self, msg, websocket: WebSocket):
        try:
            if msg.get('e') == 'kline':
                kline = msg['k']
                
                # İndikatörleri hesapla
                df = self.calculate_indicators(kline, self.indicator_settings)
                
                # Sinyalleri hesapla
                signals = self.calculate_signals(df)
                
                data = {
                    'timestamp': kline['t'],
                    'close': float(kline['c']),
                    'indicators': {
                        'rsi': float(df['rsi'].iloc[-1]),
                        'macd': float(df['macd'].iloc[-1]),
                        'macd_signal': float(df['macd_signal'].iloc[-1]),
                        'sma': float(df['sma'].iloc[-1]),
                        'ema': float(df['ema'].iloc[-1])
                    },
                    'signals': signals
                }
                
                await websocket.send_text(json.dumps(data))
                
        except Exception as e:
            logger.error(f"Veri işleme hatası: {str(e)}")

    async def start_kline_socket(self, symbol: str, interval: str):
        try:
            await self.initialize_socket()
            
            # Önceki bağlantıyı kapat
            if symbol in self.tasks:
                self.tasks[symbol].cancel()
                del self.tasks[symbol]

            # Yeni socket stream'i başlat
            socket = self.socket_manager.kline_socket(
                symbol=symbol.lower(),
                interval=interval
            )

            async with socket as stream:
                while True:
                    msg = await stream.recv()
                    for connection in self.active_connections:
                        await self.handle_socket_message(msg, connection)

        except Exception as e:
            logger.error(f"WebSocket hatası: {str(e)}")
            # Bağlantıyı yeniden kurma girişimi
            await asyncio.sleep(5)
            await self.start_kline_socket(symbol, interval)

    async def close_all(self):
        if self.client:
            await self.client.close_connection()
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()
        logger.info("Tüm bağlantılar kapatıldı")

    def calculate_indicators(self, kline, settings):
        # Tek bir mum için DataFrame oluştur
        df = pd.DataFrame([{
            'timestamp': kline['t'],
            'open': float(kline['o']),
            'high': float(kline['h']),
            'low': float(kline['l']),
            'close': float(kline['c']),
            'volume': float(kline['v'])
        }])
        
        # Tüm indikatörleri hesapla
        df = apply_indicators(df, settings)
        
        return df

    def calculate_signals(self, df):
        signals = {
            'bb_buy': False,
            'bb_sell': False,
            'rsi_buy': False,
            'rsi_sell': False,
            'macd_buy': False,
            'macd_sell': False,
            'supertrend_buy': False,
            'supertrend_sell': False,
            'dmi_buy': False,
            'dmi_sell': False
        }
        
        # Bollinger Bands sinyalleri
        if df['close'].iloc[-1] < df['bb_lower'].iloc[-1]:
            signals['bb_buy'] = True
        elif df['close'].iloc[-1] > df['bb_upper'].iloc[-1]:
            signals['bb_sell'] = True
        
        # RSI sinyalleri
        if df['rsi'].iloc[-1] < 30:
            signals['rsi_buy'] = True
        elif df['rsi'].iloc[-1] > 70:
            signals['rsi_sell'] = True
        
        # MACD sinyalleri
        if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
            signals['macd_buy'] = True
        elif df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]:
            signals['macd_sell'] = True
        
        # SuperTrend sinyalleri
        if df['close'].iloc[-1] > df['supertrend'].iloc[-1]:
            signals['supertrend_buy'] = True
        elif df['close'].iloc[-1] < df['supertrend'].iloc[-1]:
            signals['supertrend_sell'] = True
        
        # DMI sinyalleri
        if df['plus_di'].iloc[-1] > df['minus_di'].iloc[-1] and df['adx'].iloc[-1] > 25:
            signals['dmi_buy'] = True
        elif df['plus_di'].iloc[-1] < df['minus_di'].iloc[-1] and df['adx'].iloc[-1] > 25:
            signals['dmi_sell'] = True
        
        return signals
    