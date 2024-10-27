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

# Function to analyze stock data and filter based on criteria
def analyze_and_filter_stocks(stock_data):
    filtered_results = {
        "Short Term": [],
        "Medium Term": [],
        "Long Term": []
    }

    for symbol, data in stock_data.items():
        close_price = data["data"]["close"]  # Get the closing price
        pivot_levels = data["data"]["pivotLevels"]
        
        # Prepare pivot levels DataFrame with error handling for numeric conversion
        pivot_levels_df = pd.DataFrame(
            [(level["key"], 
              pd.to_numeric(level["pivotLevel"].get("pivotPoint"), errors='coerce'),
              pd.to_numeric(level["pivotLevel"].get("r1"), errors='coerce'), 
              pd.to_numeric(level["pivotLevel"].get("s1"), errors='coerce'))
             for level in pivot_levels],
            columns=["Key", "Pivot Point", "R1", "S1"]
        )

        # Drop rows with NaN values to ensure all data is numeric
        pivot_levels_df = pivot_levels_df.dropna()

        if not pivot_levels_df.empty:
            # Calculate averages for Pivot Levels
            averages = pivot_levels_df.mean().to_frame().T
            averages["Symbol"] = symbol

            # Analyze stop loss and target
            for level in pivot_levels:
                stoploss = pd.to_numeric(level["pivotLevel"].get("s1"), errors='coerce')
                target = pd.to_numeric(level["pivotLevel"].get("r1"), errors='coerce')

                # Ensure stoploss and target are valid numbers
                if pd.isna(stoploss) or pd.isna(target):
                    continue

                # Calculate stop loss and target changes
                stop_loss_change = (close_price - stoploss) / close_price * 100
                target_change = (target - close_price) / close_price * 100

                # Filtering based on term
                if stop_loss_change >= -3 and target_change >= 5:
                    filtered_results["Short Term"].append((symbol, close_price, stoploss, target, averages))

                if stop_loss_change >= -4 and target_change >= 10:
                    filtered_results["Medium Term"].append((symbol, close_price, stoploss, target, averages))

                if stop_loss_change >= -5 and target_change >= 15:
                    filtered_results["Long Term"].append((symbol, close_price, stoploss, target, averages))

    # Sort and return top 20 stocks for each term
    for term in filtered_results:
        filtered_results[term] = sorted(filtered_results[term], key=lambda x: x[1], reverse=True)[:20]

    return filtered_results

# Input for stock symbols to search
stock_symbols_input = st.text_input("Enter stock symbols separated by commas (e.g., ABB, GOOGL):")
stock_symbols = [s.strip() for s in stock_symbols_input.split(',')] if stock_symbols_input else []

if stock_symbols:
    stock_data = load_all_stock_data(stock_symbols)
    
    # Analyze and filter stocks
    filtered_stocks = analyze_and_filter_stocks(stock_data)

    # Display results
    st.title("Filtered Stocks Analysis")

    for term in ["Short Term", "Medium Term", "Long Term"]:
        st.subheader(f"{term} Stocks")
        if filtered_stocks[term]:
            results_df = pd.DataFrame(filtered_stocks[term], columns=["Symbol", "Close Price", "Stoploss", "Target", "Averages"])
            st.table(results_df[["Symbol", "Close Price", "Stoploss", "Target"]])  # Display top stocks

            # Display Pivot Levels and Averages for each stock
            for idx, row in results_df.iterrows():
                symbol = row["Symbol"]
                averages = row["Averages"]

                st.write(f"**Pivot Levels and Averages for {symbol}**")
                st.table(averages)

                # Display SMA and EMA data
                sma_df = pd.DataFrame(stock_data[symbol]["data"]["sma"])
                ema_df = pd.DataFrame(stock_data[symbol]["data"]["ema"])
                
                st.write("**Simple Moving Averages (SMA)**")
                st.table(sma_df)

                st.write("**Exponential Moving Averages (EMA)**")
                st.table(ema_df)

                # Display Moving Average Crossovers
                crossover_df = pd.DataFrame(stock_data[symbol]["data"]["crossover"])
                st.write("**Moving Average Crossovers**")
                st.table(crossover_df)

                # Display Technical Indicators
                indicators_df = pd.DataFrame(stock_data[symbol]["data"]["indicators"])
                st.write("**Technical Indicators**")
                st.table(indicators_df)

                # Stoploss and Target table for each stock
                stoploss_target_df = pd.DataFrame({
                    "Key": [row["Symbol"]],
                    "Stoploss": [row["Stoploss"]],
                    "Target": [row["Target"]]
                })
                st.write(f"**Stoploss and Target for {symbol}**")
                st.table(stoploss_target_df)

        else:
            st.write(f"No stocks meet the criteria for {term}.")
