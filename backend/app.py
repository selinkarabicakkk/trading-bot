from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fetch_data import fetch_data
from backtest_runner import BacktestRunner
import logging
import json
import asyncio
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
from pydantic import BaseModel

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS ve güvenlik ayarları
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "ws://localhost:8000",
    "ws://127.0.0.1:8000",
    "wss://localhost:8000",
    "wss://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Pydantic modelleri
class BacktestRequest(BaseModel):
    symbols: List[str]
    timeframes: List[str]
    indicators: List[Dict]

# WebSocket bağlantı yöneticisi
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_count = 0
        self.ping_interval = 30  # 30 saniye
        self.live_data_tasks = {}  # WebSocket -> Task mapping

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            self.connection_count += 1
            logger.info(f"Yeni WebSocket bağlantısı kabul edildi. Aktif bağlantı sayısı: {self.connection_count}")
            return True
        except Exception as e:
            logger.error(f"WebSocket bağlantı hatası: {str(e)}")
            return False

    def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                self.connection_count -= 1
                # Live data task'ı varsa iptal et
                if websocket in self.live_data_tasks:
                    self.live_data_tasks[websocket].cancel()
                    del self.live_data_tasks[websocket]
                logger.info(f"WebSocket bağlantısı kapatıldı. Aktif bağlantı sayısı: {self.connection_count}")
        except Exception as e:
            logger.error(f"Bağlantı kapatma hatası: {str(e)}")

    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
            return True
        except WebSocketDisconnect:
            logger.error("WebSocket bağlantısı koptu")
            await self.disconnect(websocket)
            return False
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {str(e)}")
            return False

    async def keep_alive(self, websocket: WebSocket):
        """Bağlantıyı canlı tutmak için ping gönder"""
        try:
            while True:
                await asyncio.sleep(self.ping_interval)
                await websocket.send_json({"type": "ping"})
        except Exception as e:
            logger.error(f"Ping hatası: {str(e)}")
            await self.disconnect(websocket)

async def live_data_stream(websocket: WebSocket, symbol: str, indicators: List[Dict]):
    """Canlı veri akışı ve sinyal üretimi"""
    last_signal_time = None
    last_price = None
    
    while True:
        try:
            # Canlı veri al
            df = await get_live_data(symbol)
            if df is not None:
                current_price = float(df['close'].iloc[-1])
                
                # Fiyat değişimi varsa veya ilk veri ise
                if last_price is None or abs((current_price - last_price) / last_price) > 0.0001:
                    # Sinyal üret
                    signal = await generate_trade_signal(df, indicators)
                    
                    if signal:
                        current_time = datetime.fromisoformat(signal["timestamp"])
                        
                        # Yeni sinyal kontrolü
                        if last_signal_time is None or (current_time - last_signal_time).total_seconds() > 60:
                            # Trade işle
                            trade_result = trade_manager.process_signal(signal)
                            if trade_result:
                                message_sent = await manager.send_personal_message(trade_result, websocket)
                                if not message_sent:
                                    break
                                logger.info(f"Yeni trade sinyali gönderildi: {trade_result['trade_type']} @ {trade_result['price']} (Kar/Zarar: {trade_result.get('profit', 0):.2f}%)")
                                last_signal_time = current_time
                
                last_price = current_price
            
            # 1 saniye bekle
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Canlı veri akışı hatası: {str(e)}")
            break

manager = ConnectionManager()

async def get_live_data(symbol: str, timeframe: str = "1m") -> pd.DataFrame:
    """Canlı market verilerini getir"""
    try:
        logger.info(f"Veri çekme başladı: {symbol} - {timeframe}")
        
        # Veriyi çek
        df = fetch_data(symbol, timeframe)
        if df is not None and not df.empty:
            return df
        return None
    except Exception as e:
        logger.error(f"Veri çekme hatası: {str(e)}")
        return None

async def generate_trade_signal(df: pd.DataFrame, indicators: List[Dict]) -> Dict:
    """İndikatörlere göre alım/satım sinyali üret"""
    try:
        runner = BacktestRunner()
        df_with_indicators = runner.calculate_indicators(df, indicators)
        logger.info("İndikatörler hesaplandı")
        
        # Son 5 mumu al
        last_rows = df_with_indicators.tail(5)
        
        # Her indikatör için sinyal kontrolü yap
        for ind in indicators:
            ind_type = ind['type'].lower()
            logger.info(f"İndikatör kontrolü: {ind_type}")
            
            if ind_type == 'sma':
                # SMA için özel sinyal kontrolü
                if 'sma' not in last_rows.columns:
                    logger.error("SMA kolonu bulunamadı")
                    continue
                    
                sma = last_rows['sma']
                close = last_rows['close']
                
                # Son 3 mumun kapanış ve SMA değerlerini al
                last_3_closes = close.tail(3)
                last_3_sma = sma.tail(3)
                
                # Trend yönünü belirle
                price_trend = last_3_closes.diff().mean()
                sma_trend = last_3_sma.diff().mean()
                
                logger.info(f"Trend Analizi - Fiyat Trendi: {price_trend:.2f}, SMA Trendi: {sma_trend:.2f}")
                
                # Fiyatın SMA'ya olan uzaklığını hesapla
                curr_diff = float(close.iloc[-1]) - float(sma.iloc[-1])
                diff_percentage = (curr_diff / float(sma.iloc[-1])) * 100
                
                logger.info(f"SMA Analizi - Fark: {curr_diff:.2f}, Fark Yüzdesi: {diff_percentage:.2f}%")
                
                # Sinyal koşulları
                # 1. Fiyat SMA'nın altında ve yukarı trend
                if curr_diff < 0 and price_trend > 0 and abs(diff_percentage) < 0.5:
                    trade_signal = 1
                    signal_reason = "Fiyat SMA'nın altında ve yukarı trend var"
                    logger.info(f"SMA AL sinyali: {signal_reason}")
                
                # 2. Fiyat SMA'nın üstünde ve aşağı trend
                elif curr_diff > 0 and price_trend < 0 and abs(diff_percentage) < 0.5:
                    trade_signal = -1
                    signal_reason = "Fiyat SMA'nın üstünde ve aşağı trend var"
                    logger.info(f"SMA SAT sinyali: {signal_reason}")
                
                # 3. Fiyat ve SMA çok yakın ve güçlü trend
                elif abs(diff_percentage) < 0.1 and abs(price_trend) > 5:
                    trade_signal = 1 if price_trend > 0 else -1
                    signal_reason = "Fiyat ve SMA yakın, güçlü trend var"
                    logger.info(f"SMA {'AL' if trade_signal == 1 else 'SAT'} sinyali: {signal_reason}")
                
                else:
                    logger.info("SMA sinyal yok")
                    continue
                    
                last_price = float(df['close'].iloc[-1])
                current_time = df.index[-1]
                
                logger.info(f"SMA Sinyal Bulundu - Tip: {'AL' if trade_signal == 1 else 'SAT'}")
                logger.info(f"SMA Değeri: {sma.iloc[-1]:.2f}, Fiyat: {close.iloc[-1]:.2f}")
                
                return create_signal_response(current_time, last_price, trade_signal, {
                    'SMA': {
                        'value': float(sma.iloc[-1]),
                        'price': float(close.iloc[-1]),
                        'difference': float(curr_diff),
                        'difference_percentage': float(diff_percentage),
                        'price_trend': float(price_trend),
                        'sma_trend': float(sma_trend),
                        'reason': signal_reason
                    }
                })
                
            elif ind_type == 'macd':
                # MACD için özel sinyal kontrolü
                if 'macd' not in last_rows.columns or 'macd_signal' not in last_rows.columns:
                    logger.error("MACD kolonları bulunamadı")
                    continue
                    
                macd = last_rows['macd']
                signal = last_rows['macd_signal']
                
                # MACD çizgisinin sinyal çizgisini kesme noktaları
                prev_diff = macd.iloc[-2] - signal.iloc[-2]
                curr_diff = macd.iloc[-1] - signal.iloc[-1]
                
                # Kesişim kontrolü
                if prev_diff <= 0 and curr_diff > 0:  # Alttan yukarı kesme = Alış
                    trade_signal = 1
                elif prev_diff >= 0 and curr_diff < 0:  # Üstten aşağı kesme = Satış
                    trade_signal = -1
                else:
                    continue
                    
                last_price = float(df['close'].iloc[-1])
                current_time = df.index[-1]
                
                logger.info(f"MACD Sinyal Bulundu - Tip: {'AL' if trade_signal == 1 else 'SAT'}")
                logger.info(f"MACD Değerleri - MACD: {macd.iloc[-1]:.2f}, Signal: {signal.iloc[-1]:.2f}, Fark: {curr_diff:.2f}")
                
                return create_signal_response(current_time, last_price, trade_signal, {
                    'MACD': {
                        'value': float(macd.iloc[-1]),
                        'signal_line': float(signal.iloc[-1]),
                        'difference': float(curr_diff)
                    }
                })
                
            elif ind_type == 'rsi':
                # RSI için özel sinyal kontrolü
                if 'rsi' not in last_rows.columns:
                    logger.error("RSI kolonu bulunamadı")
                    continue
                    
                rsi = last_rows['rsi']
                current_rsi = float(rsi.iloc[-1])
                prev_rsi = float(rsi.iloc[-2])
                
                # RSI değer geçişleri
                if prev_rsi <= 30 and current_rsi > 30:  # Aşırı satım bölgesinden çıkış = Alış
                    trade_signal = 1
                elif prev_rsi >= 70 and current_rsi < 70:  # Aşırı alım bölgesinden çıkış = Satış
                    trade_signal = -1
                else:
                    continue
                    
                last_price = float(df['close'].iloc[-1])
                current_time = df.index[-1]
                
                logger.info(f"RSI Sinyal Bulundu - Tip: {'AL' if trade_signal == 1 else 'SAT'}")
                logger.info(f"RSI Değeri: {current_rsi:.2f}")
                
                return create_signal_response(current_time, last_price, trade_signal, {
                    'RSI': {
                        'value': current_rsi,
                        'previous': prev_rsi
                    }
                })
                
        logger.info("Sinyal bulunamadı")
        return None
                
    except Exception as e:
        logger.error(f"Sinyal üretme hatası: {str(e)}")
        return None

def create_signal_response(current_time, price, signal, indicators):
    """Standart sinyal yanıtı oluştur"""
    return {
        "timestamp": current_time.isoformat(),
        "price": price,
        "signal": signal,
        "indicators": indicators,
        "trade_type": "BUY" if signal == 1 else "SELL",
        "marker": {
            "time": int(current_time.timestamp()),
            "position": "belowBar" if signal == 1 else "aboveBar",
            "color": "#4CAF50" if signal == 1 else "#FF5252",
            "shape": "arrowUp" if signal == 1 else "arrowDown",
            "text": "AL" if signal == 1 else "SAT"
        }
    }

class TradeManager:
    def __init__(self):
        self.last_trade = None
        self.position = None
        self.entry_price = None
        self.total_profit = 0
        self.trades = []
        self.last_signal_time = None

    def calculate_profit(self, exit_price):
        """Kar/zarar hesapla"""
        if self.position and self.entry_price:
            if self.position == "BUY":
                profit = (exit_price - self.entry_price) / self.entry_price * 100
            else:
                profit = (self.entry_price - exit_price) / self.entry_price * 100
            return round(profit, 2)
        return 0

    def process_signal(self, signal_data):
        """Sinyal işle ve kar/zarar hesapla"""
        try:
            current_signal = signal_data["signal"]
            current_price = signal_data["price"]
            current_time = datetime.fromisoformat(signal_data["timestamp"])
            
            # Aynı zamanda sinyal varsa işleme
            if self.last_signal_time and current_time <= self.last_signal_time:
                return None
                
            # Sinyal yoksa işlem yapma
            if current_signal == 0:
                return None
                
            # İlk trade veya pozisyon yoksa
            if not self.position:
                self.position = "BUY" if current_signal == 1 else "SELL"
                self.entry_price = current_price
                trade_result = {
                    **signal_data,
                    "trade_type": self.position,
                    "profit": 0
                }
                self.last_trade = trade_result
                self.last_signal_time = current_time
                logger.info(f"Yeni pozisyon açıldı: {self.position} @ {self.entry_price}")
                return trade_result
                
            # Mevcut pozisyonun tersi bir sinyal geldiyse
            if ((self.position == "BUY" and current_signal == -1) or 
                (self.position == "SELL" and current_signal == 1)):
                
                # Kar/zarar hesapla
                profit = self.calculate_profit(current_price)
                self.total_profit += profit
                
                # Yeni trade oluştur
                trade_result = {
                    **signal_data,
                    "trade_type": "SELL" if self.position == "BUY" else "BUY",
                    "profit": profit
                }
                
                logger.info(f"Pozisyon kapatıldı: {self.position} @ {current_price} (Kar/Zarar: {profit}%)")
                
                # Pozisyonu güncelle
                self.position = "BUY" if current_signal == 1 else "SELL"
                self.entry_price = current_price
                self.last_trade = trade_result
                self.last_signal_time = current_time
                
                return trade_result
                
            return None
            
        except Exception as e:
            logger.error(f"Trade işleme hatası: {str(e)}")
            return None

trade_manager = TradeManager()

@app.websocket("/ws/live-trade")
async def live_trade(websocket: WebSocket):
    connection_successful = await manager.connect(websocket)
    if not connection_successful:
        return

    # Keep-alive task'ı başlat
    keep_alive_task = asyncio.create_task(manager.keep_alive(websocket))

    try:
        # İlk parametreleri al
        init_data = await websocket.receive_text()
        trade_params = json.loads(init_data)
        symbol = trade_params.get("symbol")
        indicators = trade_params.get("indicators", [])
        
        logger.info(f"Canlı işlem başlatıldı - Sembol: {symbol}, İndikatörler: {indicators}")
        
        # Başlangıç durumunu gönder
        await manager.send_personal_message({
            "status": "success",
            "message": "Canlı işlem başlatıldı",
            "params": trade_params
        }, websocket)
        
        # Canlı veri akışı task'ını başlat
        live_data_task = asyncio.create_task(live_data_stream(websocket, symbol, indicators))
        manager.live_data_tasks[websocket] = live_data_task
        
        try:
            # Task tamamlanana kadar bekle
            await live_data_task
        except asyncio.CancelledError:
            logger.info("Canlı veri akışı durduruldu")
        
    except WebSocketDisconnect:
        logger.info("WebSocket bağlantısı client tarafından kapatıldı")
    except Exception as e:
        error_msg = f"WebSocket genel hatası: {str(e)}"
        logger.error(error_msg)
        try:
            await websocket.send_json({"error": error_msg})
        except:
            pass
    finally:
        # Task'ları temizle
        keep_alive_task.cancel()
        if websocket in manager.live_data_tasks:
            manager.live_data_tasks[websocket].cancel()
        manager.disconnect(websocket)

@app.post("/api/run-backtest")
async def run_backtest(request: BacktestRequest):
    """Backtest'i çalıştır"""
    try:
        logger.info(f"Backtest isteği alındı: {request.dict()}")
        
        if len(request.symbols) != 1:
            error_msg = "Sadece bir sembol seçilebilir"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        symbol = request.symbols[0]
        timeframe = request.timeframes[0]
        
        logger.info(f"Veri çekiliyor: {symbol} - {timeframe}")
        df = await get_live_data(symbol, timeframe)
        
        if df is None or df.empty:
            error_msg = f"Veri bulunamadı: {symbol} - {timeframe}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
            
        logger.info("Backtest başlatılıyor...")
        runner = BacktestRunner()
        result = runner.run_backtest(df, request.indicators)
        
        if not result:
            error_msg = "Backtest sonuçları alınamadı"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)

        logger.info("Backtest başarıyla tamamlandı")
        return {
            symbol: {
                timeframe: result
            }
        }

    except HTTPException as he:
        logger.error(f"HTTP hatası: {he.detail}")
        raise he
    except Exception as e:
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
