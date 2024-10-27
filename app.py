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

# Function to filter stocks based on sentiments
def filter_stocks_by_sentiment(stock_data, term):
    sentiment_stocks = []
    
    for symbol, data in stock_data.items():
        sentiments = data["data"].get("sentiments", {})
        total_bearish = sentiments.get("totalBearish", 0)
        total_bullish = sentiments.get("totalBullish", 0)
        total_neutral = sentiments.get("totalNeutral", 0)

        # Apply filtering based on term
        if (term == "Short Term" and total_bullish > 0) or \
           (term == "Medium Term" and total_bullish > 1) or \
           (term == "Long Term" and total_bullish > 2):
            sentiment_stocks.append((symbol, total_bullish, total_bearish, total_neutral))

    return sorted(sentiment_stocks, key=lambda x: (x[1], -x[2]), reverse=True)[:20]  # Top 20 based on bullishness

# Load stock data from the specified folder
data_folder = "data"  # Adjust this path if needed
stock_data = load_all_stock_data(data_folder)

# Filter stocks for each term
short_term_stocks = filter_stocks(stock_data, "Short Term")
medium_term_stocks = filter_stocks(stock_data, "Medium Term")
long_term_stocks = filter_stocks(stock_data, "Long Term")

# Load sentiment data for each term
short_term_sentiment_stocks = filter_stocks_by_sentiment(stock_data, "Short Term")
medium_term_sentiment_stocks = filter_stocks_by_sentiment(stock_data, "Medium Term")
long_term_sentiment_stocks = filter_stocks_by_sentiment(stock_data, "Long Term")

# Function to create DataFrame for stock indicators
def create_stock_dataframe(stocks):
    data = []
    for stock in stocks:
        symbol, close_price, stoploss, target, indicators = stock
        
        # Extract individual indicator values, indications
        rsi_value = indicators.get("rsi", {}).get("value", "")
        rsi_indication = indicators.get("rsi", {}).get("indication", "")
        macd_value = indicators.get("macd", {}).get("value", "")
        macd_indication = indicators.get("macd", {}).get("indication", "")
        
        # Append data
        data.append((symbol, close_price, stoploss, target, rsi_value, rsi_indication, macd_value, macd_indication))

    columns = [
        "Symbol", "Close Price", "Stoploss", "Target", 
        "RSI Value", "RSI Indication", 
        "MACD Value", "MACD Indication"
    ]
    return pd.DataFrame(data, columns=columns)

# Function to create DataFrame for sentiment-based stocks
def create_sentiment_stock_dataframe(stocks):
    data = []
    for stock in stocks:
        symbol, total_bullish, total_bearish, total_neutral = stock
        data.append((symbol, total_bullish, total_bearish, total_neutral))

    columns = ["Symbol", "Total Bullish", "Total Bearish", "Total Neutral"]
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

# Function to display sentiment-based stocks
def display_sentiment_stocks(stocks, term):
    if stocks:
        df = create_sentiment_stock_dataframe(stocks)
        st.table(df)

        # Provide option to download as Excel
        excel_file = f"{term}_sentiment_stocks.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as f:
            st.download_button("Download Excel", f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.write(f"No stocks meet the criteria for {term} based on sentiment.")

st.title("Top Filtered Stocks Based on Technicals and Sentiment")

# Display filtered stocks
st.subheader("Bullish Short Term Stocks")
display_stocks(short_term_stocks, "Short Term")

st.subheader("Bullish Medium Term Stocks")
display_stocks(medium_term_stocks, "Medium Term")

st.subheader("Bullish Long Term Stocks")
display_stocks(long_term_stocks, "Long Term")

# Display sentiment-based stocks
st.subheader("Bullish Short Term Stocks (Based on Sentiment)")
display_sentiment_stocks(short_term_sentiment_stocks, "Short Term")

st.subheader("Bullish Medium Term Stocks (Based on Sentiment)")
display_sentiment_stocks(medium_term_sentiment_stocks, "Medium Term")

st.subheader("Bullish Long Term Stocks (Based on Sentiment)")
display_sentiment_stocks(long_term_sentiment_stocks, "Long Term")
