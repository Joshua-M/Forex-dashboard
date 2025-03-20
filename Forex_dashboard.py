import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="Forex Trading Dashboard", page_icon="💹", layout="wide")

# Title with Styling
st.markdown("""
    <style>
    .big-font {
        font-size:32px !important;
        font-weight: bold;
        color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">💹 Forex Trading Dashboard - USD/JPY Analysis</p>', unsafe_allow_html=True)

# Load dataset
file_path = "USDJPY_Historical_Data.xls"
df = pd.read_csv(file_path)

# Rename columns for better readability
df.rename(columns={"Unnamed: 0": "Date"}, inplace=True)
df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
df.sort_values(by="Date", ascending=True, inplace=True)

# Sidebar Filters
st.sidebar.header("🔍 Filters")
start_date, end_date = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])

# Apply Date Filter
df_filtered = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

# Metrics with Styling
highest_price = df_filtered["High"].max()
lowest_price = df_filtered["Low"].min()
avg_volatility = (df_filtered["High"] - df_filtered["Low"]).mean()

st.markdown("### 📌 Key Forex Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("📈 Highest Price", f"{highest_price:.2f}")
col2.metric("📉 Lowest Price", f"{lowest_price:.2f}")
col3.metric("📊 Avg. Daily Volatility", f"{avg_volatility:.4f}")

# Candlestick Chart
st.markdown("### 📊 Candlestick Chart")
candle_fig = go.Figure(data=[go.Candlestick(
    x=df_filtered["Date"],
    open=df_filtered["Open"],
    high=df_filtered["High"],
    low=df_filtered["Low"],
    close=df_filtered["Close"],
    name="Candlestick"
)])
candle_fig.update_layout(title="USD/JPY Candlestick Chart", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
st.plotly_chart(candle_fig, use_container_width=True)

# Moving Averages
st.markdown("### 📈 Moving Averages")
df_filtered["7-day MA"] = df_filtered["Close"].rolling(window=7).mean()
df_filtered["30-day MA"] = df_filtered["Close"].rolling(window=30).mean()

ma_fig = px.line(df_filtered, x="Date", y=["Close", "7-day MA", "30-day MA"],
                 labels={"value": "Price", "variable": "Metric"},
                 title="USD/JPY Moving Averages")
st.plotly_chart(ma_fig, use_container_width=True)

# Bollinger Bands
st.markdown("### 📊 Bollinger Bands")
rolling_mean = df_filtered["Close"].rolling(window=20).mean()
rolling_std = df_filtered["Close"].rolling(window=20).std()
upper_band = rolling_mean + (rolling_std * 2)
lower_band = rolling_mean - (rolling_std * 2)

bollinger_fig = go.Figure()
bollinger_fig.add_trace(go.Scatter(x=df_filtered["Date"], y=upper_band, name='Upper Band', line=dict(color='red')))
bollinger_fig.add_trace(go.Scatter(x=df_filtered["Date"], y=lower_band, name='Lower Band', line=dict(color='green')))
bollinger_fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Close"], name='Closing Price', line=dict(color='blue')))

bollinger_fig.update_layout(title="USD/JPY Bollinger Bands", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
st.plotly_chart(bollinger_fig, use_container_width=True)

# MACD Indicator
st.markdown("### 📊 MACD Indicator")
def compute_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data.ewm(span=short_window, adjust=False).mean()
    long_ema = data.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal

df_filtered["MACD"], df_filtered["Signal Line"] = compute_macd(df_filtered["Close"])
macd_fig = px.line(df_filtered, x="Date", y=["MACD", "Signal Line"], title="Moving Average Convergence Divergence (MACD)")
st.plotly_chart(macd_fig, use_container_width=True)

# Automated Trading Signals
st.markdown("### 🔔 Automated Trading Signals")
if df_filtered["MACD"].iloc[-1] > df_filtered["Signal Line"].iloc[-1] and df_filtered["RSI"].iloc[-1] < 30:
    st.success("📢 Buy Signal: Momentum is shifting upwards!")
elif df_filtered["MACD"].iloc[-1] < df_filtered["Signal Line"].iloc[-1] and df_filtered["RSI"].iloc[-1] > 70:
    st.error("📢 Sell Signal: Market is overbought and momentum is shifting downwards!")
else:
    st.info("📢 No clear trading signal. Wait for better conditions.")

# Data Table
st.markdown("### 📋 Raw Data Table")
st.dataframe(df_filtered)

# Download Processed Data
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download Data", data=csv, file_name="USDJPY_Processed_Data.csv", mime="text/csv")
