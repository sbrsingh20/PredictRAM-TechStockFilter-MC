import requests
import pandas as pd
import json

# Load stock symbols from the Excel file
symbols_df = pd.read_excel('stock_symbols.xlsx')


# Define the base URL
base_url = "https://priceapi.moneycontrol.com/pricefeed/techindicator/M/"

# Define headers to mimic a browser request
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
    }
#
#
# Function to fetch and save data for a single stock symbol
def fetch_and_save_data(sc_id,stock_name,symbol):
    url = f"{base_url}{sc_id}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        #Save the data to a JSON file
        json_file = f"{symbol}_data.json"
        with open(json_file, 'w') as json_output:
            json.dump(data, json_output, indent=4)

        print(f"Data for symbol:{symbol} name:{stock_name} saved to {json_file}")
    else:
        print(f"Failed to fetch data for symbol:{symbol} name:{stock_name}. Status code: {response.status_code}")


# Loop through each symbol and fetch data
for symbol in symbols_df['Symbol']:
    try:
        symbol=symbol.replace('.NS','')
        s = requests.Session()
        s.get("https://www.nseindia.com/", headers=headers)
        nse_url=f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        print(nse_url)
        r = s.get(nse_url, headers=headers)
        isin=r.json()['metadata']['isin']

        money_control_suggestion_url = f'https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?classic=true&query={isin}&type=1&format=json'
        print(money_control_suggestion_url)
        money_control_res = requests.get(money_control_suggestion_url, headers=headers)
        sc_id = money_control_res.json()[0]['sc_id']
        stock_name = money_control_res.json()[0]['stock_name']
        fetch_and_save_data(sc_id,stock_name,symbol)
    except Exception as e:
        print(f"failed {symbol}")
        continue