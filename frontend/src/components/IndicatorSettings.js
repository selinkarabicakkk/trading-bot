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
  IconButton,
  Tooltip,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";

const AVAILABLE_INDICATORS = {
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
  macd: {
    name: "MACD",
    params: {
      fast_period: { default: 12, min: 1, max: 50, label: "Hızlı Periyot" },
      slow_period: { default: 26, min: 1, max: 100, label: "Yavaş Periyot" },
      signal_period: { default: 9, min: 1, max: 50, label: "Sinyal Periyodu" },
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
    setSelectedIndicator({ ...indicator });
    setIsSettingsDialogOpen(true);
  };

  const handleParamChange = (param, value) => {
    if (selectedIndicator) {
      const numValue = Number(value);
      const config = AVAILABLE_INDICATORS[selectedIndicator.type].params[param];

      // Değer sınırlarını kontrol et
      if (numValue >= config.min && numValue <= config.max) {
        const updatedIndicator = {
          ...selectedIndicator,
          params: {
            ...selectedIndicator.params,
            [param]: numValue,
          },
        };
        setSelectedIndicator(updatedIndicator);

        // Ana indikatör listesini güncelle
        setActiveIndicators((prev) =>
          prev.map((ind) =>
            ind.id === selectedIndicator.id ? updatedIndicator : ind
          )
        );
      }
    }
  };

  const handleSettingsClose = () => {
    setIsSettingsDialogOpen(false);
    setSelectedIndicator(null);
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
            <ListItem
              sx={{
                backgroundColor: "#1a237e",
                borderRadius: 1,
                mb: 1,
              }}
            >
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
                sx={{
                  "& .MuiListItemText-primary": {
                    color: "#ffffff",
                    fontWeight: "bold",
                  },
                  "& .MuiListItemText-secondary": {
                    color: "#b3e5fc",
                  },
                }}
              />
              <ListItemSecondaryAction>
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => handleSettingsOpen(indicator)}
                  sx={{
                    mr: 1,
                    backgroundColor: "rgba(25, 118, 210, 0.2)",
                    "&:hover": {
                      backgroundColor: "rgba(25, 118, 210, 0.3)",
                    },
                    fontWeight: "medium",
                  }}
                >
                  Ayarlar
                </Button>
                <Button
                  size="small"
                  variant="contained"
                  color="error"
                  onClick={() => handleRemoveIndicator(indicator.id)}
                  sx={{
                    backgroundColor: "rgba(211, 47, 47, 0.2)",
                    "&:hover": {
                      backgroundColor: "rgba(211, 47, 47, 0.3)",
                    },
                    fontWeight: "medium",
                  }}
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
          <Grid container spacing={2}>
            {Object.entries(AVAILABLE_INDICATORS).map(([type, config]) => (
              <Grid item xs={12} sm={6} md={4} key={type}>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={() => handleAddIndicator(type)}
                  sx={{
                    backgroundColor: "#1a237e",
                    color: "#ffffff",
                    "&:hover": {
                      backgroundColor: "#283593",
                    },
                    fontWeight: "bold",
                    py: 1.5,
                  }}
                >
                  {config.name}
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
        onClose={handleSettingsClose}
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
                      onChange={(e) => handleParamChange(param, e.target.value)}
                      inputProps={{
                        min: config.min,
                        max: config.max,
                        step: param.includes("Period") ? 1 : 1,
                      }}
                    />
                  </Grid>
                ))}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleSettingsClose}>Kapat</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Paper>
  );
};

export default IndicatorSettings;
