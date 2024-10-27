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
                filtered_stocks.append((symbol, close_price, stoploss, target))

    return sorted(filtered_stocks, key=lambda x: x[1], reverse=True)[:20]  # Top 20 stocks

# Load stock data from the specified folder
data_folder = "data"  # Adjust this path if needed
stock_data = load_all_stock_data(data_folder)

# Filter stocks for each term
short_term_stocks = filter_stocks(stock_data, "Short Term")
medium_term_stocks = filter_stocks(stock_data, "Medium Term")
long_term_stocks = filter_stocks(stock_data, "Long Term")

# Display results
st.title("Top Filtered Stocks Based on Technicals")

st.subheader("Short Term Stocks")
if short_term_stocks:
    st.table(pd.DataFrame(short_term_stocks, columns=["Symbol", "Close Price", "Stoploss", "Target"]))
else:
    st.write("No stocks meet the criteria for Short Term.")

st.subheader("Medium Term Stocks")
if medium_term_stocks:
    st.table(pd.DataFrame(medium_term_stocks, columns=["Symbol", "Close Price", "Stoploss", "Target"]))
else:
    st.write("No stocks meet the criteria for Medium Term.")

st.subheader("Long Term Stocks")
if long_term_stocks:
    st.table(pd.DataFrame(long_term_stocks, columns=["Symbol", "Close Price", "Stoploss", "Target"]))
else:
    st.write("No stocks meet the criteria for Long Term.")
