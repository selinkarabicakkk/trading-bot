# 📈 Crypto Trading and Backtesting Platform

## Overview

This project is a dynamic crypto trading and backtesting platform that enables users to analyze cryptocurrency markets, test trading strategies, and visualize data in real time. It integrates with Binance Mainnet API to provide live market data and supports various technical indicators for making informed trading decisions. The platform includes a React-based frontend, a Python Flask backend, and WebSocket connections for live data streaming.

---

## Features

### 1. **Real-Time Data Visualization**
- Visualizes real-time price data for multiple cryptocurrencies using interactive charts.
- Supports multiple timeframes: **1 Day**, **4 Hours**, **1 Hour**, and **15 Minutes**.
- WebSocket integration for continuous live data updates.

### 2. **Backtesting Functionality**
- Perform backtests on historical data over different timeframes.
- Simulates a $10,000 portfolio and evaluates strategy performance using various indicators.
- Provides detailed reports on profit/loss for each strategy.

### 3. **Technical Indicators**
The platform supports the following technical indicators:
- **RSI (Relative Strength Index)**
- **MACD (Moving Average Convergence Divergence)**
- **SMA (Simple Moving Average)**
- **EMA (Exponential Moving Average)**
- **Bollinger Bands**
- **SuperTrend**
- **DMI (Directional Movement Index)**

### 4. **Simulated Live Trading**
- Execute simulated buy and sell orders based on real-time Binance Mainnet data.
- Frontend allows users to change indicator parameters and trading signals dynamically.
- Simulates trades without placing real orders, using a hypothetical $10,000 balance.

### 5. **Dynamic User Interaction**
- No need to restart the server for changes; all adjustments are made through the frontend.
- Modify indicators, coins, and timeframes on the fly.

---

## Demo Instructions

### **Backtesting**
1. Perform backtests for the following cryptocurrencies:
   - **ETHUSDT**
   - **BTCUSDT**
   - **AVAXUSDT**
   - **SOLUSDT**
   - **RENDERUSDT**
   - **FETUSDT**
2. Evaluate the performance of different indicators over:
   - **1 Day**
   - **4 Hours**
   - **1 Hour**
   - **15 Minutes**

### **Simulated Live Trading**
1. Choose a coin and timeframe on the frontend.
2. Adjust indicator parameters as needed.
3. Execute simulated trades and observe the buy/sell signals.
4. Demonstrate at least 5 trades during the live demo.


## Technologies Used

### **Frontend**
- **React**: For building the user interface.
- **Material-UI**: For modern UI components.
- **Chart.js**: For data visualization.

### **Backend**
- **Python**: For backend logic.
- **Flask**: Lightweight web framework for API endpoints.
- **FastAPI + Uvicorn**: For WebSocket support and live data streaming.
- **Binance Python SDK**: For interacting with the Binance API.

### **Data Analysis**
- **Pandas**: For data manipulation and analysis.
- **NumPy**: For numerical operations.
- **Technical Indicators**: RSI, MACD, SMA, EMA, Bollinger Bands, SuperTrend, DMI.

### **WebSocket**
- **ThreadedWebsocketManager**: For streaming Binance market data.
- **WebSocket (FastAPI)**: For managing live connections with the frontend.

### **Others**
- **Git**: Version control.
- **Certifi**: For SSL certificate verification.
- **Virtual Environments**: Dependency management.


