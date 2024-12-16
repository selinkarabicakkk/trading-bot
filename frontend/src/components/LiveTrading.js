import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  Box,
  Button,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import TradingViewChart from "./TradingViewChart";

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  fontWeight: "bold",
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.common.white,
}));

const LiveTrading = ({ symbol, indicators }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [trades, setTrades] = useState([]);
  const [error, setError] = useState(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [stats, setStats] = useState({
    totalTrades: 0,
    winningTrades: 0,
    losingTrades: 0,
    successRate: 0,
    totalProfit: 0,
    averageProfit: 0,
  });
  const wsRef = useRef(null);
  const chartRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // WebSocket bağlantısını temizle
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const connect = useCallback(async () => {
    try {
      if (wsRef.current) {
        wsRef.current.close();
      }

      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/live-trade`;
      console.log("WebSocket bağlantısı kuruluyor:", wsUrl);

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket bağlantısı açıldı");
        setIsConnected(true);
        setError(null);
        setReconnectAttempt(0);

        const params = {
          symbol: symbol,
          indicators: indicators.map((ind) => ({
            type: ind.type,
            params: ind.params,
          })),
        };
        console.log("Gönderilen parametreler:", params);
        ws.send(JSON.stringify(params));
      };

      ws.onmessage = (event) => {
        try {
          console.log("Yeni mesaj alındı:", event.data);
          const data = JSON.parse(event.data);

          if (data.error) {
            console.error("Sunucu hatası:", data.error);
            setError(data.error);
            return;
          }

          if (data.status === "success" && data.message) {
            console.log("Durum mesajı:", data.message);
            return;
          }

          if (data.signal && data.signal !== 0) {
            console.log("Trade sinyali alındı:", data);
            const trade = {
              timestamp: data.timestamp,
              price: data.price,
              type: data.trade_type,
              profit: data.profit || 0,
              indicators: data.indicators,
            };

            setTrades((prev) => {
              const newTrades = [...prev, trade];
              console.log("Güncellenmiş trades listesi:", newTrades);
              return newTrades;
            });
            updateStats(trade);

            if (chartRef.current && data.marker) {
              console.log("Marker ekleniyor:", data.marker);
              chartRef.current.createMarker(data.marker);
            }
          }
        } catch (error) {
          console.error("Mesaj işleme hatası:", error);
          setError("Veri işleme hatası: " + error.message);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket bağlantı hatası:", error);
        setError("Bağlantı hatası oluştu. Yeniden bağlanmaya çalışılıyor...");
      };

      ws.onclose = (event) => {
        console.log("WebSocket bağlantısı kapandı:", event.code, event.reason);
        setIsConnected(false);

        // Normal kapanma değilse yeniden bağlan
        if (event.code !== 1000) {
          const nextAttempt = reconnectAttempt + 1;
          setReconnectAttempt(nextAttempt);

          // Üstel geri çekilme ile yeniden bağlanma
          const delay = Math.min(1000 * Math.pow(2, nextAttempt), 30000);
          setError(
            `Bağlantı kesildi. ${
              delay / 1000
            } saniye içinde yeniden bağlanılacak...`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            if (!isConnected) {
              console.log(`Yeniden bağlanma denemesi ${nextAttempt}...`);
              connect();
            }
          }, delay);
        }
      };
    } catch (error) {
      console.error("Bağlantı başlatma hatası:", error);
      setError("Bağlantı başlatılamadı: " + error.message);
    }
  }, [symbol, indicators, reconnectAttempt, isConnected]);

  const startLiveTrading = useCallback(() => {
    setTrades([]); // Trades listesini sıfırla
    setStats({
      totalTrades: 0,
      winningTrades: 0,
      losingTrades: 0,
      successRate: 0,
      totalProfit: 0,
      averageProfit: 0,
    });
    connect();
  }, [connect]);

  const stopLiveTrading = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, "Kullanıcı tarafından kapatıldı");
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    setIsConnected(false);
    setError(null);
    setReconnectAttempt(0);
  }, []);

  // İstatistikleri güncelle
  const updateStats = (newTrade) => {
    console.log("İstatistikler güncelleniyor:", newTrade);
    setStats((prevStats) => {
      const totalTrades = prevStats.totalTrades + 1;
      let winningTrades = prevStats.winningTrades;
      let losingTrades = prevStats.losingTrades;
      let totalProfit = prevStats.totalProfit;

      const profit = newTrade.profit || 0;
      if (profit > 0) {
        winningTrades++;
      } else if (profit < 0) {
        losingTrades++;
      }

      totalProfit += profit;

      const newStats = {
        totalTrades,
        winningTrades,
        losingTrades,
        successRate: totalTrades > 0 ? (winningTrades / totalTrades) * 100 : 0,
        totalProfit,
        averageProfit: totalTrades > 0 ? totalProfit / totalTrades : 0,
      };

      console.log("Yeni istatistikler:", newStats);
      return newStats;
    });
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Button
        variant="contained"
        color={isConnected ? "error" : "primary"}
        onClick={isConnected ? stopLiveTrading : startLiveTrading}
        disabled={!symbol || indicators.length === 0}
      >
        {isConnected ? "Canlı İşlemi Durdur" : "Canlı İşlem Başlat"}
      </Button>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}

      {isConnected && (
        <Box sx={{ mt: 2 }}>
          <Box sx={{ height: "600px", mb: 2 }}>
            <TradingViewChart
              ref={chartRef}
              symbol={symbol}
              interval="1"
              theme="dark"
            />
          </Box>

          <Typography variant="h6" gutterBottom>
            İşlem İstatistikleri
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <StyledTableCell>Toplam İşlem</StyledTableCell>
                  <StyledTableCell>Kazançlı</StyledTableCell>
                  <StyledTableCell>Zararlı</StyledTableCell>
                  <StyledTableCell>Başarı Oranı</StyledTableCell>
                  <StyledTableCell>Toplam Kar/Zarar</StyledTableCell>
                  <StyledTableCell>Ortalama Kar/Zarar</StyledTableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>{stats.totalTrades}</TableCell>
                  <TableCell>{stats.winningTrades}</TableCell>
                  <TableCell>{stats.losingTrades}</TableCell>
                  <TableCell>{stats.successRate.toFixed(2)}%</TableCell>
                  <TableCell>{stats.totalProfit.toFixed(2)}%</TableCell>
                  <TableCell>{stats.averageProfit.toFixed(2)}%</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>

          <Typography variant="h6" sx={{ mt: 2 }} gutterBottom>
            Son İşlemler
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <StyledTableCell>Tarih/Saat</StyledTableCell>
                  <StyledTableCell>İşlem</StyledTableCell>
                  <StyledTableCell>Fiyat</StyledTableCell>
                  <StyledTableCell>Kar/Zarar</StyledTableCell>
                  {indicators.map((ind, index) => (
                    <StyledTableCell key={index}>{ind.type}</StyledTableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {trades.length > 0 ? (
                  trades
                    .slice()
                    .reverse()
                    .map((trade, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          {new Date(trade.timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell
                          sx={{
                            color: trade.type === "BUY" ? "green" : "red",
                            fontWeight: "bold",
                          }}
                        >
                          {trade.type === "BUY" ? "AL" : "SAT"}
                        </TableCell>
                        <TableCell>{trade.price.toFixed(2)}</TableCell>
                        <TableCell
                          sx={{
                            color:
                              trade.profit > 0
                                ? "green"
                                : trade.profit < 0
                                ? "red"
                                : "inherit",
                            fontWeight: "bold",
                          }}
                        >
                          {trade.profit ? trade.profit.toFixed(2) + "%" : "-"}
                        </TableCell>
                        {indicators.map((ind, indIndex) => (
                          <TableCell key={indIndex}>
                            {trade.indicators[ind.type]?.value?.toFixed(2) ||
                              "-"}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4 + indicators.length} align="center">
                      Henüz işlem yapılmadı
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
    </Box>
  );
};

export default LiveTrading;
