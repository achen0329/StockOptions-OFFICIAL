from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_API_KEY
from repos.exceptions import AlphaVantageApiException  # Import the exception class

app = Flask(__name__)

# Define the available stocks to be displayed
available_stocks = ["PTON", "GME", "COIN", "ZM", "BYND", "AMC", "RBLX", "AAPL", "AMZN", "NVDA", "ACB", "SHOP", "NFLX", "DIS", "GOOG", "TSLA", "META", "MSFT"]

# ... Keep the rest of the code as is, except for the class definition ...
def get_stock_data(symbol):
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'compact'
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        raise AlphaVantageApiException(response.status_code)

    data = response.json()

    # Calculate yesterday's date in YYYY-MM-DD format
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if 'Time Series (Daily)' in data and yesterday in data['Time Series (Daily)']:
        daily_data = data['Time Series (Daily)'][yesterday]
        # Flatten the data and add the symbol
        flattened_data = {
            'date': yesterday,
            'symbol': symbol,
            'open': daily_data.get('1. open'),
            'high': daily_data.get('2. high'),
            'low': daily_data.get('3. low'),
            'close': daily_data.get('4. close'),
            'adjusted_close': daily_data.get('5. adjusted close'),  # Make sure the key matches the API response
            'volume': daily_data.get('6. volume'),
            'dividend_amount': daily_data.get('7. dividend amount'),  # Make sure the key matches the API response
            'split_coefficient': daily_data.get('8. split coefficient')  # Make sure the key matches the API response
        }
        return flattened_data
    else:
        return None


@app.route('/', methods=['GET'])
def index():
    stock_data_list = []
    for symbol in available_stocks:
        try:
            stock_data = get_stock_data(symbol)
            if stock_data is not None:
                stock_data_list.append(stock_data)
        except AlphaVantageApiException as e:
            # Handle the API exception, maybe log it, and continue
            print(e)
            continue  # Skip the current iteration and proceed with the next symbol
    return render_template('index.html', stock_data_list=stock_data_list)

@app.errorhandler(AlphaVantageApiException)
def handle_api_error(error):
    # Here you would define what to do when an AlphaVantageApiException is raised
    # For the purpose of this example, let's just pass the message to an error template.
    return render_template('error.html', message=error), 500



if __name__ == '__main__':
    app.run(debug=True)
