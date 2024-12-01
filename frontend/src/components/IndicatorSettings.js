import React, { useState, useEffect } from "react";
import {
  Grid,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  TextField,
  Box,
  Divider,
} from "@mui/material";

const AVAILABLE_INDICATORS = {
  bollinger: {
    name: "Bollinger Bands",
    params: {
      period: { default: 20, min: 1, max: 100, label: "Periyot" },
      stdDev: { default: 2, min: 0.1, max: 5, label: "Standart Sapma" },
    },
  },
  rsi: {
    name: "RSI",
    params: {
      period: { default: 14, min: 1, max: 50, label: "Periyot" },
      overbought: { default: 70, min: 50, max: 100, label: "Aşırı Alım" },
      oversold: { default: 30, min: 0, max: 50, label: "Aşırı Satım" },
    },
  },
  sma: {
    name: "SMA",
    params: {
      period: { default: 20, min: 1, max: 200, label: "Periyot" },
    },
  },
  ema: {
    name: "EMA",
    params: {
      period: { default: 20, min: 1, max: 200, label: "Periyot" },
    },
  },
  macd: {
    name: "MACD",
    params: {
      fastPeriod: { default: 12, min: 1, max: 50, label: "Hızlı Periyot" },
      slowPeriod: { default: 26, min: 1, max: 100, label: "Yavaş Periyot" },
      signalPeriod: { default: 9, min: 1, max: 50, label: "Sinyal Periyodu" },
    },
  },
  supertrend: {
    name: "SuperTrend",
    params: {
      period: { default: 10, min: 1, max: 50, label: "Periyot" },
      multiplier: { default: 3, min: 0.1, max: 10, label: "Çarpan" },
    },
  },
  dmi: {
    name: "DMI",
    params: {
      period: { default: 14, min: 1, max: 50, label: "Periyot" },
      adxPeriod: { default: 14, min: 1, max: 50, label: "ADX Periyodu" },
    },
  },
};

const IndicatorSettings = ({ onIndicatorsChange }) => {
  const [activeIndicators, setActiveIndicators] = useState([]);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isSettingsDialogOpen, setIsSettingsDialogOpen] = useState(false);
  const [selectedIndicator, setSelectedIndicator] = useState(null);

  useEffect(() => {
    onIndicatorsChange(activeIndicators);
  }, [activeIndicators, onIndicatorsChange]);

  const handleAddIndicator = (type) => {
    const newIndicator = {
      id: Date.now(),
      type,
      params: Object.fromEntries(
        Object.entries(AVAILABLE_INDICATORS[type].params).map(
          ([key, value]) => [key, value.default]
        )
      ),
    };
    setActiveIndicators((prev) => [...prev, newIndicator]);
    setIsAddDialogOpen(false);
  };

  const handleRemoveIndicator = (id) => {
    setActiveIndicators((prev) => prev.filter((ind) => ind.id !== id));
  };

  const handleSettingsOpen = (indicator) => {
    setSelectedIndicator(indicator);
    setIsSettingsDialogOpen(true);
  };

  const handleParamChange = (id, param, value) => {
    setActiveIndicators((prev) =>
      prev.map((ind) =>
        ind.id === id
          ? {
              ...ind,
              params: { ...ind.params, [param]: Number(value) },
            }
          : ind
      )
    );
  };

  return (
    <Paper elevation={4} sx={{ p: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">İndikatörler</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setIsAddDialogOpen(true)}
        >
          + İndikatör Ekle
        </Button>
      </Box>

      <List>
        {activeIndicators.map((indicator) => (
          <React.Fragment key={indicator.id}>
            <ListItem>
              <ListItemText
                primary={AVAILABLE_INDICATORS[indicator.type].name}
                secondary={Object.entries(indicator.params)
                  .map(
                    ([key, value]) =>
                      `${
                        AVAILABLE_INDICATORS[indicator.type].params[key].label
                      }: ${value}`
                  )
                  .join(", ")}
              />
              <ListItemSecondaryAction>
                <Button
                  size="small"
                  onClick={() => handleSettingsOpen(indicator)}
                  sx={{ mr: 1 }}
                >
                  Ayarlar
                </Button>
                <Button
                  size="small"
                  color="error"
                  onClick={() => handleRemoveIndicator(indicator.id)}
                >
                  Sil
                </Button>
              </ListItemSecondaryAction>
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>

      <Dialog
        open={isAddDialogOpen}
        onClose={() => setIsAddDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>İndikatör Ekle</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {Object.entries(AVAILABLE_INDICATORS).map(([key, indicator]) => (
              <Grid item xs={12} sm={6} key={key}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => handleAddIndicator(key)}
                >
                  {indicator.name}
                </Button>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAddDialogOpen(false)}>İptal</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={isSettingsDialogOpen}
        onClose={() => setIsSettingsDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        {selectedIndicator && (
          <>
            <DialogTitle>
              {AVAILABLE_INDICATORS[selectedIndicator.type].name} Ayarları
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {Object.entries(
                  AVAILABLE_INDICATORS[selectedIndicator.type].params
                ).map(([param, config]) => (
                  <Grid item xs={12} sm={6} key={param}>
                    <TextField
                      fullWidth
                      label={config.label}
                      type="number"
                      value={selectedIndicator.params[param]}
                      onChange={(e) =>
                        handleParamChange(
                          selectedIndicator.id,
                          param,
                          e.target.value
                        )
                      }
                      inputProps={{
                        min: config.min,
                        max: config.max,
                        step: param.includes("Period") ? 1 : 0.1,
                      }}
                    />
                  </Grid>
                ))}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setIsSettingsDialogOpen(false)}>
                Kapat
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Paper>
  );
};

export default IndicatorSettings;
