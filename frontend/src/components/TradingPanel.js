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
} from "@mui/material";

function TradingPanel({ balance, position, trades, currentPrice, lastSignal }) {
  return (
    <Grid item xs={12}>
      <Paper elevation={4} sx={{ p: 2, mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6">
              Bakiye: {balance.toFixed(2)} USDT
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="h6">
              Güncel Fiyat: {currentPrice?.toFixed(2)} USDT
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
              Son İşlemler
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tip</TableCell>
                  <TableCell>Fiyat</TableCell>
                  <TableCell>Miktar</TableCell>
                  <TableCell>Sinyal</TableCell>
                  <TableCell>Kar/Zarar</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {trades.slice(-5).map((trade, index) => (
                  <TableRow key={index}>
                    <TableCell>{trade.type}</TableCell>
                    <TableCell>{trade.price.toFixed(2)}</TableCell>
                    <TableCell>{trade.amount.toFixed(8)}</TableCell>
                    <TableCell>{trade.signal}</TableCell>
                    <TableCell>
                      {trade.pnl ? `${trade.pnl.toFixed(2)} USDT` : "-"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Grid>
        </Grid>
      </Paper>
    </Grid>
  );
}

export default TradingPanel;
