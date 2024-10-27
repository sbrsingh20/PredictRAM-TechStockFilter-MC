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

# Function to filter stocks based on defined trading conditions
def filter_stocks(stock_data, term):
    filtered_stocks = []

    for symbol, data in stock_data.items():
        # Ensure the indicators key exists and is a list
        if "data" in data and "indicators" in data["data"]:
            indicators = {indicator["id"]: float(indicator["value"]) for indicator in data["data"]["indicators"] if "value" in indicator}
            
            # Extract indicator values with default of 0 if they do not exist
            rsi = indicators.get("rsi", 0)
            macd = indicators.get("macd", 0)
            stochastic = indicators.get("stochastic", 0)
            roc = indicators.get("roc", 0)
            cci = indicators.get("cci", 0)

            # Apply filtering based on term conditions
            if term == "Short Term":
                if (rsi > 50 and 55 <= rsi <= 70 and
                    macd > 0 and
                    stochastic > 20 and 50 <= stochastic <= 80 and
                    roc > 0 and
                    cci > 100):
                    filtered_stocks.append(symbol)

            elif term == "Medium Term":
                if (50 < rsi <= 70 and
                    macd > 0 and
                    stochastic > 20 and stochastic <= 80 and
                    roc > 0 and
                    cci > 100):
                    filtered_stocks.append(symbol)

            elif term == "Long Term":
                if (rsi > 50 and 60 <= rsi <= 70 and
                    macd > 0 and
                    stochastic > 20 and 40 <= stochastic <= 70 and
                    roc > 0 and
                    cci > 100):
                    filtered_stocks.append(symbol)

    return filtered_stocks[:20]  # Return top 20 stocks

# Load stock data from the specified folder
data_folder = "data"  # Adjust this path if needed
stock_data = load_all_stock_data(data_folder)

# Filter stocks for each term
short_term_stocks = filter_stocks(stock_data, "Short Term")
medium_term_stocks = filter_stocks(stock_data, "Medium Term")
long_term_stocks = filter_stocks(stock_data, "Long Term")

# Display results
st.title("Top Filtered Stocks Based on Trading Conditions")

st.subheader("Short Term Stocks")
if short_term_stocks:
    st.table(pd.DataFrame(short_term_stocks, columns=["Symbol"]))
else:
    st.write("No stocks meet the criteria for Short Term.")

st.subheader("Medium Term Stocks")
if medium_term_stocks:
    st.table(pd.DataFrame(medium_term_stocks, columns=["Symbol"]))
else:
    st.write("No stocks meet the criteria for Medium Term.")

st.subheader("Long Term Stocks")
if long_term_stocks:
    st.table(pd.DataFrame(long_term_stocks, columns=["Symbol"]))
else:
    st.write("No stocks meet the criteria for Long Term.")
