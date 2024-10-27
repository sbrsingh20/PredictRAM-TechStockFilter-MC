import streamlit as st
import pandas as pd
import json
import os

# Function to load JSON data for all stocks in the data folder
def load_all_stock_data(data_folder):
    stock_data = {}
    for filename in os.listdir(data_folder):
        if filename.endswith("_data.json"):
            symbol = filename.split("_")[0]  # Extract stock symbol from filename
            file_path = os.path.join(data_folder, filename)
            try:
                with open(file_path, "r") as file:
                    stock_data[symbol] = json.load(file)
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")
    return stock_data

# Function to filter stocks based on criteria
def filter_stocks(stock_data, term):
    filtered_stocks = []
    
    for symbol, data in stock_data.items():
        close_price = data["data"]["close"]  # Get the closing price
        pivot_levels = data["data"]["pivotLevels"]
        indicators = {ind["id"]: ind for ind in data["data"].get("indicators", [])}  # Get technical indicators

        # Calculate stop loss and target prices from the pivot levels
        for level in pivot_levels:
            stoploss = float(level["pivotLevel"]["s1"])
            target = float(level["pivotLevel"]["r1"])

            # Calculate stop loss and target changes
            stop_loss_change = (close_price - stoploss) / close_price * 100
            target_change = (target - close_price) / close_price * 100

            # Apply filtering based on term
            if (term == "Short Term" and stop_loss_change >= -3 and target_change >= 5) or \
               (term == "Medium Term" and stop_loss_change >= -4 and target_change >= 10) or \
               (term == "Long Term" and stop_loss_change >= -5 and target_change >= 15):
                filtered_stocks.append((symbol, close_price, stoploss, target, indicators))

    return sorted(filtered_stocks, key=lambda x: x[1], reverse=True)[:20]  # Top 20 stocks

# Load stock data from the specified folder
data_folder = "data"  # Adjust this path if needed
stock_data = load_all_stock_data(data_folder)

# Filter stocks for each term
short_term_stocks = filter_stocks(stock_data, "Short Term")
medium_term_stocks = filter_stocks(stock_data, "Medium Term")
long_term_stocks = filter_stocks(stock_data, "Long Term")

# Function to create DataFrame for display
def create_stock_dataframe(stocks):
    data = []
    for stock in stocks:
        symbol, close_price, stoploss, target, indicators = stock
        
        # Extract individual indicator values
        rsi = indicators.get("rsi", {}).get("value", "")
        macd = indicators.get("macd", {}).get("value", "")
        stochastic = indicators.get("stochastic", {}).get("value", "")
        roc = indicators.get("roc", {}).get("value", "")
        cci = indicators.get("cci", {}).get("value", "")
        williams_r = indicators.get("williamsR", {}).get("value", "")
        mfi = indicators.get("mfi", {}).get("value", "")
        atr = indicators.get("atr", {}).get("value", "")
        adx = indicators.get("adx", {}).get("value", "")
        ub = indicators.get("bollinger", {}).get("value", [{}])[0].get("value", "")
        lb = indicators.get("bollinger", {}).get("value", [{}])[1].get("value", "")
        sma20 = indicators.get("bollinger", {}).get("value", [{}])[2].get("value", "")
        
        data.append((symbol, close_price, stoploss, target, rsi, macd, stochastic, roc, cci, 
                      williams_r, mfi, atr, adx, ub, lb, sma20))

    columns = ["Symbol", "Close Price", "Stoploss", "Target", 
               "RSI", "MACD", "Stochastic", "ROC", "CCI", 
               "Williamson%R", "MFI", "ATR", "ADX", "UB", "LB", "SMA20"]
    return pd.DataFrame(data, columns=columns)

# Function to display stocks and provide Excel export option
def display_stocks(stocks, term):
    if stocks:
        df = create_stock_dataframe(stocks)
        st.table(df)

        # Provide option to download as Excel
        excel_file = f"{term}_stocks.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as f:
            st.download_button("Download Excel", f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.write(f"No stocks meet the criteria for {term}.")

st.title("Top Filtered Stocks Based on Technicals")

st.subheader("Short Term Stocks")
display_stocks(short_term_stocks, "Short Term")

st.subheader("Medium Term Stocks")
display_stocks(medium_term_stocks, "Medium Term")

st.subheader("Long Term Stocks")
display_stocks(long_term_stocks, "Long Term")
