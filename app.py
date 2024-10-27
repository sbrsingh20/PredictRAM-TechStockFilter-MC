import pandas as pd
import json

# Sample JSON data (replace this with your actual data loading logic)
stock_data_json = '''
{
    "ABB": {
        "code": "200",
        "message": "Success",
        "data": {
            "open": 4105.5,
            "high": 4180.0,
            "low": 4078.05,
            "close": 4167.5,
            "pclose": 4008.5,
            "volume": 183988,
            "reqDate": "2023-11",
            "feedTime": "1699026834",
            "scId": "ABB",
            "exchangeId": "N",
            "pivotLevels": [
                {
                    "key": "Classic",
                    "pivotLevel": {
                        "pivotPoint": "4287.98",
                        "r1": "4488.27",
                        "r2": "4878.28",
                        "r3": "5078.57",
                        "s1": "3897.97",
                        "s2": "3697.68",
                        "s3": "3307.67"
                    }
                },
                {
                    "key": "Fibonacci",
                    "pivotLevel": {
                        "pivotPoint": "4287.98",
                        "r1": "4513.48",
                        "r2": "4652.79",
                        "r3": "4878.28",
                        "s1": "4062.49",
                        "s2": "3923.18",
                        "s3": "3697.68"
                    }
                },
                {
                    "key": "Camarilla",
                    "pivotLevel": {
                        "pivotPoint": "4287.98",
                        "r1": "4152.36",
                        "r2": "4206.47",
                        "r3": "4260.58",
                        "s1": "4044.14",
                        "s2": "3990.03",
                        "s3": "3935.92"
                    }
                }
            ],
            "sma": [
                {"key": "5", "value": "4241.72", "indication": "Bearish"},
                {"key": "10", "value": "3975.80", "indication": "Bullish"},
                {"key": "20", "value": "3362.14", "indication": "Bullish"}
            ],
            "ema": [
                {"key": "5", "value": "4122.22", "indication": "Bullish"},
                {"key": "10", "value": "3918.03", "indication": "Bullish"}
            ],
            "crossover": [
                {"key": "5_20", "indication": "Bullish", "period": "Short Term"},
                {"key": "20_50", "indication": "Bullish", "period": "Medium Term"}
            ],
            "indicators": [
                {"id": "rsi", "value": "68.79", "indication": "Bullish"},
                {"id": "macd", "value": "597.41", "indication": "Bullish"}
            ]
        }
    }
}
'''

# Load stock data from JSON
stock_data = json.loads(stock_data_json)

def analyze_and_filter_stocks(stock_data):
    filtered_results = {
        "Short Term": [],
        "Medium Term": [],
        "Long Term": []
    }

    for symbol, data in stock_data.items():
        close_price = data["data"]["close"]  # Get the closing price
        pivot_levels = data["data"]["pivotLevels"]

        # Prepare pivot levels DataFrame
        pivot_levels_df = pd.DataFrame(
            [(level["key"], 
              float(level["pivotLevel"]["pivotPoint"]),
              float(level["pivotLevel"]["r1"]),
              float(level["pivotLevel"]["s1"]))
             for level in pivot_levels],
            columns=["Key", "Pivot Point", "R1", "S1"]
        )

        # Calculate averages for Pivot Levels
        averages = pivot_levels_df.mean(numeric_only=True).to_frame().T
        averages["Symbol"] = symbol

        # Analyze stop loss and target
        for level in pivot_levels:
            key = level["key"]
            stoploss = float(level["pivotLevel"]["s1"])
            target = float(level["pivotLevel"]["r1"])

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

# Run the analysis
filtered_stocks = analyze_and_filter_stocks(stock_data)

# Output results
for term, stocks in filtered_stocks.items():
    print(f"\n{term} Stocks:")
    for stock in stocks:
        symbol, close_price, stoploss, target, averages = stock
        print(f"Symbol: {symbol}, Close Price: {close_price}, Stop Loss: {stoploss}, Target: {target}, Averages: {averages.values.tolist()}")

