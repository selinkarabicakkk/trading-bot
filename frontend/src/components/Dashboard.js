import React, { useState } from "react";
import {
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  Container,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import BacktestResults from "./BacktestResults";
import IndicatorSettings from "./IndicatorSettings";
import TradingPanel from "./TradingPanel";
import TradingViewChart from "./TradingViewChart";
import Layout from "./Layout";

function Dashboard() {
  const [backtestResults, setBacktestResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState("BTCUSDT");
  const [selectedTimeframe, setSelectedTimeframe] = useState("60");
  const [activeIndicators, setActiveIndicators] = useState([]);

  const allSymbols = [
    "ETHUSDT",
    "BTCUSDT",
    "AVAXUSDT",
    "SOLUSDT",
    "RENDERUSDT",
    "FETUSDT",
  ];
  const allTimeframes = [
    { value: "15", label: "15 Dakika" },
    { value: "60", label: "1 Saat" },
    { value: "240", label: "4 Saat" },
    { value: "D", label: "1 Gün" },
  ];

  // Trading Panel için örnek veriler
  const tradingData = {
    balance: 10000,
    trades: [],
    lastSignal: null,
  };

  const handleIndicatorsChange = (indicators) => {
    setActiveIndicators(indicators);
  };

  const fetchBacktestResults = async () => {
    if (activeIndicators.length === 0) {
      alert("Lütfen en az bir indikatör ekleyin!");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/run-backtest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbols: [selectedSymbol],
          timeframes: [selectedTimeframe],
          indicators: activeIndicators.map((ind) => ({
            type: ind.type,
            params: ind.params,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setBacktestResults(null);
      setTimeout(() => {
        setBacktestResults(data);
      }, 100);
    } catch (error) {
      console.error("Backtest sonuçları alınamadı:", error);
      setBacktestResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Container maxWidth="xl">
        <Grid container spacing={3}>
          {/* Sol Taraf */}
          <Grid item xs={12} md={8}>
            {/* Sembol ve Timeframe Seçimi */}
            <Box sx={{ mb: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Sembol</InputLabel>
                    <Select
                      value={selectedSymbol}
                      onChange={(e) => {
                        setSelectedSymbol(e.target.value);
                        setBacktestResults(null);
                      }}
                      label="Sembol"
                    >
                      {allSymbols.map((symbol) => (
                        <MenuItem key={symbol} value={symbol}>
                          {symbol}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Zaman Aralığı</InputLabel>
                    <Select
                      value={selectedTimeframe}
                      onChange={(e) => {
                        setSelectedTimeframe(e.target.value);
                        setBacktestResults(null);
                      }}
                      label="Zaman Aralığı"
                    >
                      {allTimeframes.map((tf) => (
                        <MenuItem key={tf.value} value={tf.value}>
                          {tf.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Box>

            {/* TradingView Grafiği */}
            <Box sx={{ mb: 3 }}>
              <Paper
                elevation={4}
                sx={{
                  height: "600px",
                  overflow: "hidden",
                }}
              >
                <TradingViewChart
                  key={`${selectedSymbol}-${selectedTimeframe}-${
                    backtestResults ? "backtest" : "initial"
                  }`}
                  symbol={selectedSymbol}
                  interval={selectedTimeframe}
                  theme="dark"
                  backtestResults={backtestResults}
                />
              </Paper>
            </Box>

            {/* Trading Panel */}
            <Box sx={{ mb: 3 }}>
              <TradingPanel
                backtestResults={backtestResults}
                selectedSymbol={selectedSymbol}
                selectedTimeframe={selectedTimeframe}
              />
            </Box>
          </Grid>

          {/* Sağ Taraf */}
          <Grid item xs={12} md={4}>
            {/* İndikatör Ayarları */}
            <IndicatorSettings onIndicatorsChange={handleIndicatorsChange} />

            {/* Backtest Bölümü */}
            <Paper elevation={4} sx={{ p: 2, mt: 3 }}>
              <Box sx={{ mb: 2, display: "flex", justifyContent: "center" }}>
                <Button
                  variant="contained"
                  onClick={fetchBacktestResults}
                  disabled={loading || !selectedSymbol || !selectedTimeframe}
                  size="large"
                  fullWidth
                >
                  {loading ? "İşlem Yapılıyor..." : "Backtest Başlat"}
                </Button>
              </Box>

              {loading ? (
                <Box sx={{ display: "flex", justifyContent: "center", p: 3 }}>
                  <Typography>İşlem yapılıyor, lütfen bekleyin...</Typography>
                </Box>
              ) : backtestResults ? (
                <BacktestResults
                  results={backtestResults}
                  selectedTimeframe={selectedTimeframe}
                />
              ) : (
                <Typography align="center">
                  Backtest başlatmak için butona tıklayın.
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Layout>
  );
}

export default Dashboard;
