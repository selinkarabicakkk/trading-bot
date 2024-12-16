import React from "react";
import {
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableContainer,
  Box,
} from "@mui/material";

function TradingPanel({ backtestResults, selectedSymbol, selectedTimeframe }) {
  if (
    !backtestResults ||
    !backtestResults[selectedSymbol] ||
    !backtestResults[selectedSymbol][selectedTimeframe]
  ) {
    return (
      <Grid item xs={12}>
        <Paper elevation={4} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            İşlem Paneli
          </Typography>
          <Typography color="text.secondary">
            Backtest sonuçları bekleniyor...
          </Typography>
        </Paper>
      </Grid>
    );
  }

  const timeframeData = backtestResults[selectedSymbol][selectedTimeframe];
  const trades = timeframeData.trades || [];
  const lastTrade = trades.length > 0 ? trades[trades.length - 1] : null;

  const currentBalance = lastTrade ? lastTrade.balance : 10000;

  const formatNumber = (num) => {
    return new Intl.NumberFormat("tr-TR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      useGrouping: false,
    }).format(num);
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const day = date.getDate().toString().padStart(2, "0");
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, "0");
    const minutes = date.getMinutes().toString().padStart(2, "0");
    return `${day}.${month}.${year} ${hours}:${minutes}`;
  };

  return (
    <Grid item xs={12}>
      <Paper elevation={4} sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          İşlem Paneli
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography
              variant="h6"
              noWrap
              sx={{
                width: "100%",
                overflow: "visible",
              }}
            >
              Başlangıç Bakiyesi: 10000.00 USDT
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography
              variant="h6"
              noWrap
              sx={{
                color: currentBalance >= 10000 ? "success.main" : "error.main",
                width: "100%",
                overflow: "visible",
              }}
            >
              Güncel Bakiye: {formatNumber(currentBalance)} USDT
            </Typography>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Tüm İşlemler ({trades.length})
            </Typography>
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>İşlem No</TableCell>
                    <TableCell>Tarih</TableCell>
                    <TableCell>Tip</TableCell>
                    <TableCell>Fiyat</TableCell>
                    <TableCell>Kar/Zarar</TableCell>
                    <TableCell>Bakiye</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trades.map((trade, index) => (
                    <TableRow key={index}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>{formatDate(trade.timestamp)}</TableCell>
                      <TableCell>{trade.type}</TableCell>
                      <TableCell>{formatNumber(trade.price)}</TableCell>
                      <TableCell
                        sx={{
                          color:
                            trade.trade_profit >= 0
                              ? "success.main"
                              : "error.main",
                        }}
                      >
                        {trade.type === "SELL" &&
                          `${formatNumber(trade.trade_profit)} USDT`}
                      </TableCell>
                      <TableCell>{formatNumber(trade.balance)} USDT</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        </Box>
      </Paper>
    </Grid>
  );
}

export default TradingPanel;
