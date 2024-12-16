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
import LiveTrading from "./LiveTrading";

function Dashboard() {
  const [backtestResults, setBacktestResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState("BTCUSDT");
  const [selectedTimeframe, setSelectedTimeframe] = useState("60");
  const [activeIndicators, setActiveIndicators] = useState([]);
  const [showLiveTrading, setShowLiveTrading] = useState(false);

  const allSymbols = [
    "ETHUSDT",
    "BTCUSDT",
    "AVAXUSDT",
    "SOLUSDT",
    "RENDERUSDT",
    "FETUSDT",
  ];
  const allTimeframes = ["15", "60", "240", "D"];

  const timeframeLabels = {
    15: "15 Dakika",
    60: "1 Saat",
    240: "4 Saat",
    D: "1 Gün",
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
                    value={selectedSymbol}
                    label="Sembol"
                    onChange={(e) => setSelectedSymbol(e.target.value)}
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
                    value={selectedTimeframe}
                    label="Interval"
                    onChange={(e) => setSelectedTimeframe(e.target.value)}
                  >
                    {allTimeframes.map((tf) => (
                      <MenuItem key={tf} value={tf}>
                        {timeframeLabels[tf]}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Button
                  variant="contained"
                  color={showLiveTrading ? "error" : "primary"}
                  onClick={() => setShowLiveTrading(!showLiveTrading)}
                  sx={{ minWidth: 120 }}
                >
                  {showLiveTrading ? "Canlı İşlemi Kapat" : "Canlı İşlem"}
                </Button>
              </Paper>
            </Box>

            {/* Canlı İşlem veya TradingView Grafiği */}
            {showLiveTrading ? (
              <LiveTrading
                symbol={selectedSymbol}
                indicators={activeIndicators.map((ind) => ({
                  type: ind.type,
                  params: ind.params,
                }))}
              />
            ) : (
              <>
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
              </>
            )}
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
