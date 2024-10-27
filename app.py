import streamlit as st
import pandas as pd
import json
import os

# Function to load JSON data for multiple symbols
def load_all_stock_data(symbols):
    stock_data = {}
    for symbol in symbols:
        try:
            file_path = f"data/{symbol}_data.json"
            with open(file_path, "r") as file:
                stock_data[symbol] = json.load(file)
        except FileNotFoundError:
            continue  # Skip if file is not found
    return stock_data

# Function to filter stocks based on criteria
def filter_stocks(stock_data, term):
    filtered_stocks = []
    
    for symbol, data in stock_data.items():
        close_price = data["data"]["close"]  # Get the closing price
        pivot_levels = data["data"]["pivotLevels"]

        for level in pivot_levels:
            key = level["key"]
            stoploss = float(level["pivotLevel"]["s1"])
            target = float(level["pivotLevel"]["r1"])

            # Calculate stop loss and target changes
            stop_loss_change = (close_price - stoploss) / close_price * 100
            target_change = (target - close_price) / close_price * 100

            if term == "Short Term":
                if stop_loss_change >= -3 and target_change >= 5:
                    filtered_stocks.append((symbol, close_price, stoploss, target))

            elif term == "Medium Term":
                if stop_loss_change >= -4 and target_change >= 10:
                    filtered_stocks.append((symbol, close_price, stoploss, target))

            elif term == "Long Term":
                if stop_loss_change >= -5 and target_change >= 15:
                    filtered_stocks.append((symbol, close_price, stoploss, target))

    # Sort and return top 20 stocks for the term
    return sorted(filtered_stocks, key=lambda x: x[1], reverse=True)[:20]

# Input for stock symbols to search
stock_symbols_input = st.text_input("Enter stock symbols separated by commas (e.g., ABB, GOOGL):")
stock_symbols = [s.strip() for s in stock_symbols_input.split(',')] if stock_symbols_input else []

if stock_symbols:
    stock_data = load_all_stock_data(stock_symbols)

    # Filter stocks for each term
    short_term_stocks = filter_stocks(stock_data, "Short Term")
    medium_term_stocks = filter_stocks(stock_data, "Medium Term")
    long_term_stocks = filter_stocks(stock_data, "Long Term")

    # Display results
    st.title("Filtered Stocks")

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
