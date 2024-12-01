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
  const [selectedSymbols, setSelectedSymbols] = useState(["BTCUSDT"]);
  const [selectedTimeframes, setSelectedTimeframes] = useState(["1d"]);
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
    { value: "1", label: "1 Dakika" },
    { value: "5", label: "5 Dakika" },
    { value: "15", label: "15 Dakika" },
    { value: "30", label: "30 Dakika" },
    { value: "60", label: "1 Saat" },
    { value: "240", label: "4 Saat" },
    { value: "D", label: "1 Gün" },
    { value: "W", label: "1 Hafta" },
    { value: "M", label: "1 Ay" },
  ];

  // Trading Panel için örnek veriler
  const tradingData = {
    balance: 10000,
    position: null,
    trades: [],
    currentPrice: 45000,
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
          symbols: selectedSymbols,
          timeframes: selectedTimeframes,
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
      setBacktestResults(data);
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
            {/* Sembol ve Interval Seçici */}
            <Box sx={{ mb: 3 }}>
              <Paper elevation={4} sx={{ p: 2, display: "flex", gap: 2 }}>
                <FormControl sx={{ flex: 2 }}>
                  <InputLabel>Sembol</InputLabel>
                  <Select
                    multiple
                    value={selectedSymbols}
                    label="Sembol"
                    onChange={(e) => setSelectedSymbols(e.target.value)}
                  >
                    {allSymbols.map((symbol) => (
                      <MenuItem key={symbol} value={symbol}>
                        {symbol}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl sx={{ flex: 1 }}>
                  <InputLabel>Interval</InputLabel>
                  <Select
                    multiple
                    value={selectedTimeframes}
                    label="Interval"
                    onChange={(e) => setSelectedTimeframes(e.target.value)}
                  >
                    {allTimeframes.map((tf) => (
                      <MenuItem key={tf.value} value={tf.value}>
                        {tf.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Paper>
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
                  symbol={selectedSymbols[0]}
                  interval={selectedTimeframes[0]}
                  theme="dark"
                />
              </Paper>
            </Box>

            {/* Trading Panel */}
            <Box sx={{ mb: 3 }}>
              <TradingPanel {...tradingData} />
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
                  disabled={
                    loading ||
                    selectedSymbols.length === 0 ||
                    selectedTimeframes.length === 0
                  }
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
                <BacktestResults results={backtestResults} />
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
