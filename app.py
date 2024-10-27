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

# Function to filter bearish stocks based on sentiment
def filter_bearish_stocks(stock_data, term):
    bearish_stocks = []
    
    for symbol, data in stock_data.items():
        sentiments = data["data"].get("sentiments", {})
        bearish_count = sentiments.get("movingAverageSentiment", {}).get("bearishCount", 0)
        total_bearish = sentiments.get("totalBearish", 0)

        # Check conditions based on term
        if (term == "Short Term" and bearish_count > 0) or \
           (term == "Medium Term" and bearish_count > 1) or \
           (term == "Long Term" and total_bearish > 2):
            bearish_stocks.append((symbol, bearish_count, total_bearish))

    return sorted(bearish_stocks, key=lambda x: (x[1], x[2]), reverse=True)[:20]  # Top 20 bearish stocks

# Load stock data from the specified folder
data_folder = "data"  # Adjust this path if needed
stock_data = load_all_stock_data(data_folder)

# Filter stocks for each term
short_term_stocks = filter_stocks(stock_data, "Short Term")
medium_term_stocks = filter_stocks(stock_data, "Medium Term")
long_term_stocks = filter_stocks(stock_data, "Long Term")

# Filter bearish stocks for each term
short_term_bearish = filter_bearish_stocks(stock_data, "Short Term")
medium_term_bearish = filter_bearish_stocks(stock_data, "Medium Term")
long_term_bearish = filter_bearish_stocks(stock_data, "Long Term")

# Function to create DataFrame for stock indicators
def create_stock_dataframe(stocks):
    data = []
    for stock in stocks:
        symbol, close_price, stoploss, target, indicators = stock
        
        # Extract individual indicator values, indications, and periods
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

# Function to display bearish stocks
def display_bearish_stocks(bearish_stocks, term):
    if bearish_stocks:
        df = pd.DataFrame(bearish_stocks, columns=["Symbol", "Bearish Count", "Total Bearish"])
        st.table(df)
    else:
        st.write(f"No bearish stocks meet the criteria for {term}.")

st.title("Top Filtered Stocks Based on Technicals")

# Display filtered stocks
st.subheader("Short Term Stocks")
display_stocks(short_term_stocks, "Short Term")

st.subheader("Medium Term Stocks")
display_stocks(medium_term_stocks, "Medium Term")

st.subheader("Long Term Stocks")
display_stocks(long_term_stocks, "Long Term")

# Display bearish stocks
st.subheader("Bearish Short Term Stocks")
display_bearish_stocks(short_term_bearish, "Short Term")

st.subheader("Bearish Medium Term Stocks")
display_bearish_stocks(medium_term_bearish, "Medium Term")

st.subheader("Bearish Long Term Stocks")
display_bearish_stocks(long_term_bearish, "Long Term")
