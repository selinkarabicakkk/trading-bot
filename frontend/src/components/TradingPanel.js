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
} from "@mui/material";

function TradingPanel({ backtestResults, selectedSymbol, selectedTimeframe }) {
  if (
    !backtestResults ||
    !backtestResults[selectedSymbol] ||
    !backtestResults[selectedSymbol][selectedTimeframe]
  ) {
    return (
      <Grid item xs={12}>
        <Paper elevation={4} sx={{ p: 2, mb: 4 }}>
          <Typography variant="body1" align="center">
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
  const position = null;

  const formatNumber = (num) => {
    if (num === undefined || num === null) return "0.00";
    return new Intl.NumberFormat("tr-TR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  return (
    <Grid item xs={12}>
      <Paper elevation={4} sx={{ p: 2, mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6">
              Başlangıç Bakiyesi: 10000.00 USDT
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography
              variant="h6"
              sx={{
                color: currentBalance >= 10000 ? "success.main" : "error.main",
              }}
            >
              Güncel Bakiye: {formatNumber(currentBalance)} USDT
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography
              variant="h6"
              color={position ? "success.main" : "text.primary"}
            >
              {position
                ? `Pozisyon: ${position.amount} @ ${position.entryPrice}`
                : "Pozisyon Yok"}
            </Typography>
          </Grid>

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
                      <TableCell>
                        {new Date(trade.timestamp).toLocaleString("tr-TR")}
                      </TableCell>
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
        </Grid>
      </Paper>
    </Grid>
  );
}

export default TradingPanel;
