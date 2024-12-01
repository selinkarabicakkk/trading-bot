import React from "react";
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
} from "@mui/material";

const BacktestResults = ({ results }) => {
  if (!results || Object.keys(results).length === 0) {
    return (
      <Typography variant="body1" align="center">
        Backtest sonucu bulunamadı.
      </Typography>
    );
  }

  const formatNumber = (num) => {
    return new Intl.NumberFormat("tr-TR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  const getResultColor = (value) => {
    return value >= 0 ? "success.main" : "error.main";
  };

  return (
    <Box>
      {Object.entries(results).map(([symbol, timeframes]) => (
        <Accordion key={symbol} defaultExpanded>
          <AccordionSummary
            expandIcon={
              <Button size="small" sx={{ minWidth: "auto", p: 0 }}>
                ▼
              </Button>
            }
          >
            <Typography variant="h6">{symbol}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Zaman Aralığı</TableCell>
                    <TableCell align="right">Başlangıç Fiyatı ($)</TableCell>
                    <TableCell align="right">Bitiş Fiyatı ($)</TableCell>
                    <TableCell align="right">Fiyat Değişimi (%)</TableCell>
                    <TableCell align="right">Toplam Kar/Zarar ($)</TableCell>
                    <TableCell align="right">
                      Strateji Performansı (%)
                    </TableCell>
                    <TableCell align="right">İşlem Hacmi ($)</TableCell>
                    <TableCell align="right">İşlem Sayısı</TableCell>
                    <TableCell align="right">Başarılı İşlem</TableCell>
                    <TableCell align="right">Başarı Oranı (%)</TableCell>
                    <TableCell align="right">Max Drawdown (%)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(timeframes).map(([timeframe, data]) => (
                    <TableRow key={timeframe}>
                      <TableCell component="th" scope="row">
                        {timeframe}
                      </TableCell>
                      <TableCell align="right">
                        {formatNumber(data.start_price)}
                      </TableCell>
                      <TableCell align="right">
                        {formatNumber(data.end_price)}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          color: getResultColor(data.price_change_percentage),
                        }}
                      >
                        {formatNumber(data.price_change_percentage)}%
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ color: getResultColor(data.total_profit) }}
                      >
                        {formatNumber(data.total_profit)}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          color: getResultColor(data.total_profit_percentage),
                        }}
                      >
                        {formatNumber(data.total_profit_percentage)}%
                      </TableCell>
                      <TableCell align="right">
                        {formatNumber(data.total_volume)}
                      </TableCell>
                      <TableCell align="right">{data.total_trades}</TableCell>
                      <TableCell align="right">{data.winning_trades}</TableCell>
                      <TableCell
                        align="right"
                        sx={{ color: getResultColor(data.win_rate - 50) }}
                      >
                        {formatNumber(data.win_rate)}%
                      </TableCell>
                      <TableCell align="right" sx={{ color: "error.main" }}>
                        {formatNumber(data.max_drawdown)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Typography variant="caption" sx={{ mt: 1, display: "block" }}>
              Kullanılan İndikatörler:{" "}
              {Object.values(timeframes)[0].indicators_used.join(", ")}
            </Typography>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default BacktestResults;
