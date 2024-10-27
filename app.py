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

# Function to read market cap data from Excel file
def load_market_cap_data(file_path):
    market_cap_data = pd.read_excel(file_path)
    return market_cap_data.set_index("symbol")["marketCap"].to_dict()

# Function to filter stocks based on market cap
def filter_by_market_cap(stock_data, market_cap_range):
    filtered_data = {}
    for symbol, data in stock_data.items():
        market_cap = market_cap_dict.get(symbol, 0)
        if market_cap_range[0] <= market_cap <= market_cap_range[1]:
            filtered_data[symbol] = data
    return filtered_data

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

# Function to filter bearish stocks based on sentiment
def filter_bearish_stocks(stock_data, term):
    bearish_stocks = []
    
    for symbol, data in stock_data.items():
        sentiments = data["data"].get("sentiments", {})
        bearish_count = sentiments.get("movingAverageSentiment", {}).get("bearishCount", 0)
        total_bearish = sentiments.get("totalBearish", 0)
        indicators = {ind["id"]: ind for ind in data["data"].get("indicators", [])}  # Get technical indicators

        # Check conditions based on term
        if (term == "Short Term" and bearish_count > 0) or \
           (term == "Medium Term" and bearish_count > 1) or \
           (term == "Long Term" and total_bearish > 2):
            bearish_stocks.append((symbol, bearish_count, total_bearish, indicators))

    return sorted(bearish_stocks, key=lambda x: (x[1], x[2]), reverse=True)[:20]  # Top 20 bearish stocks

# Load stock data from the specified folder
data_folder = "data"  # Adjust this path if needed
stock_data = load_all_stock_data(data_folder)

# Load market cap data from Excel file
market_cap_file = "SymbolWithMarketCap.xlsx"  # Adjust this path if needed
market_cap_dict = load_market_cap_data(market_cap_file)

# Slider for market cap selection
min_market_cap = min(market_cap_dict.values())
max_market_cap = max(market_cap_dict.values())
market_cap_range = st.slider(
    "Select Market Cap Range",
    min_value=min_market_cap,
    max_value=max_market_cap,
    value=(min_market_cap, max_market_cap)
)

# Filter stock data by selected market cap range
filtered_stock_data = filter_by_market_cap(stock_data, market_cap_range)

# Check if any stocks were found after filtering
if not filtered_stock_data:
    st.write("No stocks found within the selected market cap range.")
else:
    # Filter stocks for each term based on the filtered stock data
    short_term_stocks = filter_stocks(filtered_stock_data, "Short Term")
    medium_term_stocks = filter_stocks(filtered_stock_data, "Medium Term")
    long_term_stocks = filter_stocks(filtered_stock_data, "Long Term")

    # Filter bearish stocks for each term based on the filtered stock data
    short_term_bearish = filter_bearish_stocks(filtered_stock_data, "Short Term")
    medium_term_bearish = filter_bearish_stocks(filtered_stock_data, "Medium Term")
    long_term_bearish = filter_bearish_stocks(filtered_stock_data, "Long Term")

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
            stochastic_value = indicators.get("stochastic", {}).get("value", "")
            stochastic_indication = indicators.get("stochastic", {}).get("indication", "")
            roc_value = indicators.get("roc", {}).get("value", "")
            roc_indication = indicators.get("roc", {}).get("indication", "")
            cci_value = indicators.get("cci", {}).get("value", "")
            cci_indication = indicators.get("cci", {}).get("indication", "")
            williams_r_value = indicators.get("williamsR", {}).get("value", "")
            williams_r_indication = indicators.get("williamsR", {}).get("indication", "")
            mfi_value = indicators.get("mfi", {}).get("value", "")
            mfi_indication = indicators.get("mfi", {}).get("indication", "")
            atr_value = indicators.get("atr", {}).get("value", "")
            atr_indication = indicators.get("atr", {}).get("indication", "")
            adx_value = indicators.get("adx", {}).get("value", "")
            adx_indication = indicators.get("adx", {}).get("indication", "")
            
            # For Bollinger Bands
            bollinger = indicators.get("bollinger", {}).get("value", [{}])
            ub_value = bollinger[0].get("value", "")
            lb_value = bollinger[1].get("value", "")
            sma20_value = bollinger[2].get("value", "")
            
            # Append data
            data.append((symbol, close_price, stoploss, target, 
                          rsi_value, rsi_indication, 
                          macd_value, macd_indication, 
                          stochastic_value, stochastic_indication, 
                          roc_value, roc_indication, 
                          cci_value, cci_indication, 
                          williams_r_value, williams_r_indication, 
                          mfi_value, mfi_indication, 
                          atr_value, atr_indication, 
                          adx_value, adx_indication, 
                          ub_value, lb_value, sma20_value))

        columns = [
            "Symbol", "Close Price", "Stoploss", "Target", 
            "RSI Value", "RSI Indication", 
            "MACD Value", "MACD Indication", 
            "Stochastic Value", "Stochastic Indication", 
            "ROC Value", "ROC Indication", 
            "CCI Value", "CCI Indication", 
            "Williamson%R Value", "Williamson%R Indication", 
            "MFI Value", "MFI Indication", 
            "ATR Value", "ATR Indication", 
            "ADX Value", "ADX Indication", 
            "UB Value", "LB Value", "SMA20 Value"
        ]
        return pd.DataFrame(data, columns=columns)

    # Function to create DataFrame for bearish stocks with indicators
    def create_bearish_stock_dataframe(stocks):
        data = []
        for stock in stocks:
            symbol, bearish_count, total_bearish, indicators = stock
            
            rsi_value = indicators.get("rsi", {}).get("value", "")
            rsi_indication = indicators.get("rsi", {}).get("indication", "")
            macd_value = indicators.get("macd", {}).get("value", "")
            macd_indication = indicators.get("macd", {}).get("indication", "")
            stochastic_value = indicators.get("stochastic", {}).get("value", "")
            stochastic_indication = indicators.get("stochastic", {}).get("indication", "")
            roc_value = indicators.get("roc", {}).get("value", "")
            roc_indication = indicators.get("roc", {}).get("indication", "")
            cci_value = indicators.get("cci", {}).get("value", "")
            cci_indication = indicators.get("cci", {}).get("indication", "")
            williams_r_value = indicators.get("williamsR", {}).get("value", "")
            williams_r_indication = indicators.get("williamsR", {}).get("indication", "")
            mfi_value = indicators.get("mfi", {}).get("value", "")
            mfi_indication = indicators.get("mfi", {}).get("indication", "")
            atr_value = indicators.get("atr", {}).get("value", "")
            atr_indication = indicators.get("atr", {}).get("indication", "")
            adx_value = indicators.get("adx", {}).get("value", "")
            adx_indication = indicators.get("adx", {}).get("indication", "")
            
            # For Bollinger Bands
            bollinger = indicators.get("bollinger", {}).get("value", [{}])
            ub_value = bollinger[0].get("value", "")
            lb_value = bollinger[1].get("value", "")
            sma20_value = bollinger[2].get("value", "")
            
            # Append data
            data.append((symbol, bearish_count, total_bearish, 
                          rsi_value, rsi_indication, 
                          macd_value, macd_indication, 
                          stochastic_value, stochastic_indication, 
                          roc_value, roc_indication, 
                          cci_value, cci_indication, 
                          williams_r_value, williams_r_indication, 
                          mfi_value, mfi_indication, 
                          atr_value, atr_indication, 
                          adx_value, adx_indication, 
                          ub_value, lb_value, sma20_value))

        columns = [
            "Symbol", "Bearish Count", "Total Bearish", 
            "RSI Value", "RSI Indication", 
            "MACD Value", "MACD Indication", 
            "Stochastic Value", "Stochastic Indication", 
            "ROC Value", "ROC Indication", 
            "CCI Value", "CCI Indication", 
            "Williamson%R Value", "Williamson%R Indication", 
            "MFI Value", "MFI Indication", 
            "ATR Value", "ATR Indication", 
            "ADX Value", "ADX Indication", 
            "UB Value", "LB Value", "SMA20 Value"
        ]
        return pd.DataFrame(data, columns=columns)

    # Display results
    st.title("Top Filtered Stocks Based on Technicals")

    st.subheader("Short Term Stocks")
    if short_term_stocks:
        st.table(create_stock_dataframe(short_term_stocks))
    else:
        st.write("No stocks meet the criteria for Short Term.")

    st.subheader("Medium Term Stocks")
    if medium_term_stocks:
        st.table(create_stock_dataframe(medium_term_stocks))
    else:
        st.write("No stocks meet the criteria for Medium Term.")

    st.subheader("Long Term Stocks")
    if long_term_stocks:
        st.table(create_stock_dataframe(long_term_stocks))
    else:
        st.write("No stocks meet the criteria for Long Term.")

    # Display bearish stocks
    st.subheader("Bearish Short Term Stocks")
    if short_term_bearish:
        st.table(create_bearish_stock_dataframe(short_term_bearish))
    else:
        st.write("No bearish stocks meet the criteria for Short Term.")

    st.subheader("Bearish Medium Term Stocks")
    if medium_term_bearish:
        st.table(create_bearish_stock_dataframe(medium_term_bearish))
    else:
        st.write("No bearish stocks meet the criteria for Medium Term.")

    st.subheader("Bearish Long Term Stocks")
    if long_term_bearish:
        st.table(create_bearish_stock_dataframe(long_term_bearish))
    else:
        st.write("No bearish stocks meet the criteria for Long Term.")
