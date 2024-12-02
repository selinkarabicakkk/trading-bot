import React, { useEffect, useRef, useCallback } from "react";
import { Box } from "@mui/material";

let tvScriptLoadingPromise;

const intervalMap = {
  1: "1",
  5: "5",
  15: "15",
  30: "30",
  60: "60",
  240: "240",
  D: "1D",
  W: "1W",
  M: "1M",
};

const TradingViewChart = ({
  symbol = "BTCUSDT",
  theme = "dark",
  interval = "D",
  backtestResults = null,
}) => {
  const onLoadScriptRef = useRef();
  const chartRef = useRef(null);
  const widgetRef = useRef(null);

  const drawBacktestSignals = useCallback(
    (widget) => {
      console.log("=== MARKER ÇIZIM BAŞLANGICI ===");
      console.log("Widget durumu:", widget ? "Hazır" : "Hazır değil");
      console.log("Backtest sonuçları:", backtestResults);
      console.log("Seçili sembol:", symbol);
      console.log("Seçili interval:", interval);

      // Önce mevcut tüm şekilleri temizle
      try {
        const shapes = widget.chart().getAllShapes();
        console.log("Mevcut şekil sayısı:", shapes.length);
        shapes.forEach((shape) => widget.chart().removeEntity(shape));
        console.log("Mevcut şekiller temizlendi");
      } catch (error) {
        console.error("Şekiller temizlenirken hata:", error);
      }

      if (
        !backtestResults ||
        !backtestResults[symbol] ||
        !backtestResults[symbol][interval] ||
        !backtestResults[symbol][interval].trades
      ) {
        console.error("Backtest sonuçları eksik veya hatalı:", {
          hasBacktestResults: !!backtestResults,
          hasSymbol: backtestResults ? !!backtestResults[symbol] : false,
          hasInterval:
            backtestResults && backtestResults[symbol]
              ? !!backtestResults[symbol][interval]
              : false,
          hasTrades:
            backtestResults &&
            backtestResults[symbol] &&
            backtestResults[symbol][interval]
              ? !!backtestResults[symbol][interval].trades
              : false,
        });
        return;
      }

      const trades = backtestResults[symbol][interval].trades;
      console.log(`Toplam işlem sayısı: ${trades.length}`);
      console.log("İşlemler:", trades);

      trades.forEach((trade, index) => {
        try {
          const signalTime = new Date(trade.timestamp).getTime() / 1000;
          const price = trade.price;
          const isBuy = trade.type === "BUY";

          console.log(`İşlem ${index + 1} marker oluşturuluyor:`, {
            type: trade.type,
            time: new Date(trade.timestamp).toLocaleString(),
            price: price,
            signalTime: signalTime,
          });

          // İşlem marker'ı
          widget.chart().createShape(
            {
              time: signalTime,
              price: price,
              text: isBuy ? "B" : "S",
              overrides: {
                text: isBuy ? "B" : "S",
                backgroundColor: isBuy ? "#26a69a" : "#ef5350",
                borderColor: isBuy ? "#26a69a" : "#ef5350",
                fontFamily: "Trebuchet MS",
                fontSize: 16,
                fontWeight: "bold",
                textColor: "#ffffff",
                size: 2,
                borderWidth: 1,
                fixedSize: true,
              },
            },
            {
              shape: "circle",
              lock: true,
              disableSelection: true,
              disableSave: true,
              disableUndo: true,
              zIndex: 100,
            }
          );
          console.log(`İşlem ${index + 1} marker başarıyla oluşturuldu`);

          // Satış işlemlerinde kar/zarar gösterimi
          if (trade.type === "SELL" && trade.trade_profit) {
            const profitColor = trade.trade_profit >= 0 ? "#26a69a" : "#ef5350";
            const profitText = `${
              trade.trade_profit >= 0 ? "+" : ""
            }${trade.trade_profit.toFixed(2)}`;

            console.log(`İşlem ${index + 1} kar/zarar gösterimi:`, {
              profit: trade.trade_profit,
              text: profitText,
            });

            widget.chart().createShape(
              {
                time: signalTime,
                price: price * 1.002,
                text: profitText,
                overrides: {
                  backgroundColor: "transparent",
                  borderColor: "transparent",
                  fontFamily: "Trebuchet MS",
                  fontSize: 12,
                  fontWeight: "bold",
                  textColor: profitColor,
                },
              },
              {
                shape: "text",
                lock: true,
                disableSelection: true,
                disableSave: true,
                disableUndo: true,
                zIndex: 100,
              }
            );
            console.log(
              `İşlem ${index + 1} kar/zarar gösterimi başarıyla oluşturuldu`
            );
          }
        } catch (error) {
          console.error(`İşlem ${index + 1} için hata:`, error);
        }
      });

      console.log("=== MARKER ÇIZIM TAMAMLANDI ===");
    },
    [backtestResults, symbol, interval]
  );

  const createWidget = useCallback(() => {
    if (
      document.getElementById("tradingview-widget") &&
      "TradingView" in window
    ) {
      try {
        const mappedInterval = intervalMap[interval] || "D";
        console.log("Kullanılan interval:", mappedInterval);

        const widgetOptions = {
          autosize: true,
          symbol: `BINANCE:${symbol}`,
          interval: mappedInterval,
          timezone: "Etc/UTC",
          theme: theme,
          style: "1",
          locale: "tr",
          toolbar_bg: theme === "dark" ? "#131722" : "#f1f3f6",
          enable_publishing: false,
          hide_top_toolbar: true,
          hide_side_toolbar: true,
          allow_symbol_change: false,
          container_id: "tradingview-widget",
          save_image: false,
          studies: [],
          disabled_features: [
            "widget_logo",
            "header_widget_dom_node",
            "header_symbol_search",
            "header_resolutions",
            "header_chart_type",
            "header_settings",
            "header_indicators",
            "header_compare",
            "header_undo_redo",
            "header_screenshot",
            "timeframes_toolbar",
            "volume_force_overlay",
            "show_interval_dialog_on_key_press",
            "legend_widget",
            "main_series_scale_menu",
            "scales_context_menu",
            "show_hide_button_in_legend",
            "source_selection_in_legend",
            "create_volume_indicator_by_default",
            "volume_force_overlay",
          ],
          enabled_features: ["hide_left_toolbar_by_default"],
          overrides: {
            "mainSeriesProperties.candleStyle.upColor": "#26a69a",
            "mainSeriesProperties.candleStyle.downColor": "#ef5350",
            "mainSeriesProperties.candleStyle.drawWick": true,
            "mainSeriesProperties.candleStyle.drawBorder": true,
            "mainSeriesProperties.candleStyle.borderColor": "#378658",
            "mainSeriesProperties.candleStyle.borderUpColor": "#26a69a",
            "mainSeriesProperties.candleStyle.borderDownColor": "#ef5350",
            "mainSeriesProperties.candleStyle.wickUpColor": "#26a69a",
            "mainSeriesProperties.candleStyle.wickDownColor": "#ef5350",
            "paneProperties.background":
              theme === "dark" ? "#131722" : "#ffffff",
            "paneProperties.vertGridProperties.color":
              theme === "dark" ? "#363c4e" : "#e1e3eb",
            "paneProperties.horzGridProperties.color":
              theme === "dark" ? "#363c4e" : "#e1e3eb",
            "scalesProperties.textColor":
              theme === "dark" ? "#9db2bd" : "#131722",
          },
          loading_screen: {
            backgroundColor: theme === "dark" ? "#131722" : "#ffffff",
            foregroundColor: theme === "dark" ? "#2962ff" : "#2962ff",
          },
        };

        console.log("Widget oluşturuluyor...");
        const widget = new window.TradingView.widget(widgetOptions);
        chartRef.current = widget;

        widget.onChartReady = () => {
          console.log("Grafik hazır");
          widgetRef.current = widget;

          if (backtestResults) {
            setTimeout(() => {
              drawBacktestSignals(widget);
            }, 1000);
          }
        };
      } catch (error) {
        console.error("TradingView widget oluşturulurken hata:", error);
      }
    }
  }, [interval, symbol, theme, backtestResults, drawBacktestSignals]);

  useEffect(() => {
    onLoadScriptRef.current = createWidget;

    if (!tvScriptLoadingPromise) {
      tvScriptLoadingPromise = new Promise((resolve) => {
        const script = document.createElement("script");
        script.id = "tradingview-widget-loading-script";
        script.src = "https://s3.tradingview.com/tv.js";
        script.type = "text/javascript";
        script.onload = resolve;
        script.onerror = () => {
          console.error("TradingView script yüklenemedi");
          resolve();
        };
        document.head.appendChild(script);
      });
    }

    tvScriptLoadingPromise
      .then(() => onLoadScriptRef.current && onLoadScriptRef.current())
      .catch((error) => {
        console.error("TradingView widget yüklenirken hata:", error);
      });

    return () => {
      onLoadScriptRef.current = null;
      if (chartRef.current) {
        try {
          const container = document.getElementById("tradingview-widget");
          if (container && container.firstChild) {
            container.removeChild(container.firstChild);
          }
          chartRef.current = null;
          widgetRef.current = null;
        } catch (e) {
          console.error("Chart temizlenirken hata:", e);
        }
      }
    };
  }, [createWidget]);

  return (
    <Box
      id="tradingview-widget"
      sx={{
        width: "100%",
        height: "600px",
        "& iframe": {
          border: "none !important",
        },
      }}
    />
  );
};

export default TradingViewChart;
