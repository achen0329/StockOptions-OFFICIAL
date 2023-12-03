# stock_api.py in repos folder

import requests
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_API_KEY
from repos.exceptions import AlphaVantageApiException

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

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if 'Time Series (Daily)' in data and yesterday in data['Time Series (Daily)']:
        daily_data = data['Time Series (Daily)'][yesterday]
        flattened_data = {
            'date': yesterday,
            'symbol': symbol,
            'open': daily_data.get('1. open'),
            'high': daily_data.get('2. high'),
            'low': daily_data.get('3. low'),
            'close': daily_data.get('4. close'),
            'adjusted_close': daily_data.get('5. adjusted close'),
            'volume': daily_data.get('6. volume'),
            'dividend_amount': daily_data.get('7. dividend amount'),
            'split_coefficient': daily_data.get('8. split coefficient')
        }
        return flattened_data
    else:
        return None
