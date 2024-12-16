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
} from "@mui/material";

const BacktestResults = ({ results, selectedTimeframe }) => {
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

  const calculatePriceChange = (startPrice, endPrice) => {
    if (!startPrice || !endPrice) return 0;
    return ((endPrice - startPrice) / startPrice) * 100;
  };

  const timeframeLabels = {
    15: "15 Dakika",
    60: "1 Saat",
    240: "4 Saat",
    D: "1 Gün",
  };

  return (
    <Box>
      {Object.entries(results).map(([symbol, timeframes]) => {
        const timeframeData = timeframes[selectedTimeframe];
        if (!timeframeData) return null;

        const priceChange = calculatePriceChange(
          timeframeData.start_price,
          timeframeData.end_price
        );

        return (
          <Box key={symbol}>
            <Typography variant="h6" gutterBottom>
              {symbol} -{" "}
              {timeframeLabels[selectedTimeframe] || selectedTimeframe}
            </Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Başlangıç Fiyatı ($)</TableCell>
                    <TableCell>Bitiş Fiyatı ($)</TableCell>
                    <TableCell>Fiyat Değişimi (%)</TableCell>
                    <TableCell>Toplam Kar/Zarar ($)</TableCell>
                    <TableCell>İşlem Sayısı</TableCell>
                    <TableCell>Başarılı İşlem</TableCell>
                    <TableCell>Başarı Oranı (%)</TableCell>
                    <TableCell>Max Drawdown (%)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>
                      {formatNumber(timeframeData.start_price)}
                    </TableCell>
                    <TableCell>
                      {formatNumber(timeframeData.end_price)}
                    </TableCell>
                    <TableCell
                      sx={{
                        color: getResultColor(priceChange),
                      }}
                    >
                      {formatNumber(priceChange)}%
                    </TableCell>
                    <TableCell
                      sx={{
                        color: getResultColor(timeframeData.total_profit),
                      }}
                    >
                      {formatNumber(timeframeData.total_profit)}
                    </TableCell>
                    <TableCell>{timeframeData.total_trades || 0}</TableCell>
                    <TableCell>{timeframeData.winning_trades || 0}</TableCell>
                    <TableCell
                      sx={{
                        color: getResultColor(
                          (timeframeData.win_rate || 0) - 50
                        ),
                      }}
                    >
                      {formatNumber(timeframeData.win_rate)}%
                    </TableCell>
                    <TableCell sx={{ color: "error.main" }}>
                      {formatNumber(timeframeData.max_drawdown)}%
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
            <Typography variant="caption" sx={{ mt: 1, display: "block" }}>
              Kullanılan İndikatörler:{" "}
              {timeframeData?.indicators_used?.join(", ") || ""}
            </Typography>
            {timeframeData?.trades && timeframeData.trades.length > 0 && (
              <Typography
                variant="caption"
                sx={{ mt: 1, display: "block", color: "text.secondary" }}
              >
                Son İşlem:{" "}
                {new Date(
                  timeframeData.trades[
                    timeframeData.trades.length - 1
                  ].timestamp
                ).toLocaleString()}
              </Typography>
            )}
          </Box>
        );
      })}
    </Box>
  );
};

export default BacktestResults;
