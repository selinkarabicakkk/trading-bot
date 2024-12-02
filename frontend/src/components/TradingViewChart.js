import React, { useEffect, useRef } from "react";
import { Box } from "@mui/material";

let tvScriptLoadingPromise;

const TradingViewChart = ({
  symbol = "BTCUSDT",
  theme = "dark",
  interval = "D",
}) => {
  const onLoadScriptRef = useRef();
  const chartRef = useRef();
  const widgetRef = useRef();

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

    function createWidget() {
      if (
        document.getElementById("tradingview-widget") &&
        "TradingView" in window
      ) {
        new window.TradingView.widget({
          autosize: true,
          symbol: `BINANCE:${symbol}`,
          interval: interval,
          timezone: "Etc/UTC",
          theme: theme,
          style: "1",
          locale: "tr",
          toolbar_bg: "#f1f3f6",
          enable_publishing: false,
          allow_symbol_change: true,
          container_id: "tradingview-widget",
          hide_side_toolbar: false,
          studies: [
            "RSI@tv-basicstudies",
            "MASimple@tv-basicstudies",
            "MACD@tv-basicstudies",
          ],
        });
      }
    }
  }, [symbol, theme, interval]);

  return (
    <Box
      id="tradingview-widget"
      sx={{
        width: "100%",
        height: "600px",
      }}
    />
  );
};

export default TradingViewChart;
