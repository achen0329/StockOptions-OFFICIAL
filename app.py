from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_API_KEY
from repos.exceptions import AlphaVantageApiException  # Import the exception class

###################################################
# Stock real time data to MongonDB Compass
import pymongo

myClient = pymongo.MongoClient("mongodb://localhost:27017/")
myStockDBName = myClient["stockDataBase"]

myStockDB2Week = myStockDBName["historical2WeekData"]
myStockDBDaily = myStockDBName["dailyData"]

# End of Stock real time data to MongonDB Compass
###################################################


app = Flask(__name__)

# Define the available stocks to be displayed
available_stocks = ["PTON", "GME", "COIN", "ZM", "BYND", "AMC", "RBLX", "AAPL", "AMZN", "NVDA", "ACB", "SHOP", "NFLX", "DIS", "GOOG", "TSLA", "META", "MSFT"]

# ... Keep the rest of the code as is, except for the class definition ...


def get_stock_data_for_two_weeks(symbol):
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'full'  # Changed to 'full' to get more data
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        raise AlphaVantageApiException(response.status_code)

    data = response.json()
    time_series = data.get('Time Series (Daily)', {})

    # Sort the dates and get the last 10 trading days
    sorted_dates = sorted(time_series.keys(), reverse=True)[:10]
    last_10_days_data = [time_series[date] for date in sorted_dates]
    
    return last_10_days_data

def calculate_two_week_average(stock_data):
    total = sum(float(day_data['4. close']) for day_data in stock_data)
    average = total / len(stock_data)
    return round(average, 2)


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
    time_series = data.get('Time Series (Daily)', {})

    # Function to get the last weekday
    def get_last_weekday(date):
        while date.weekday() > 4:  # Mon-Fri are 0-4
            date -= timedelta(days=1)
        return date

    last_weekday = get_last_weekday(datetime.now() - timedelta(days=1))

    # Check for the last available data
    while last_weekday.strftime('%Y-%m-%d') not in time_series:
        last_weekday = get_last_weekday(last_weekday - timedelta(days=1))

    last_date_str = last_weekday.strftime('%Y-%m-%d')
    if last_date_str in time_series:
        daily_data = time_series[last_date_str]
        flattened_data = {
            'date': last_date_str,
            'symbol': symbol,
            'open': round(float(daily_data.get('1. open')), 2),
            'high': round(float(daily_data.get('2. high')), 2),
            'low': round(float(daily_data.get('3. low')), 2),
            'close': round(float(daily_data.get('4. close')), 2),
        }

        # Now call get_stock_data_for_two_weeks to get data for the two-week average
        two_weeks_data = get_stock_data_for_two_weeks(symbol)
        current_price = round(float(two_weeks_data[0]['4. close']), 2)
        two_week_average = round(calculate_two_week_average(two_weeks_data), 2)
    
        
        # Now append the current price and two-week average to the flattened data
        flattened_data['current_price'] = current_price
        flattened_data['two_week_average'] = two_week_average
        
        return flattened_data
    else:
        return None

def get_historical_stock_data(symbol):
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'full'
    }

    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        raise AlphaVantageApiException(response.status_code)

    data = response.json()
    time_series = data.get('Time Series (Daily)', {})
    
    two_weeks_ago = (datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d')
    last_10_days_data = {date: details for date, details in time_series.items() if date >= two_weeks_ago}

    # Sort the dates and get the last 10 trading days
    sorted_dates = sorted(last_10_days_data.keys(), reverse=True)[:10]
    last_10_days_data_sorted = [last_10_days_data[date] for date in sorted_dates]
    
    current_price = round(float(last_10_days_data_sorted[0]['4. close']), 2)
    two_week_average = calculate_two_week_average(last_10_days_data_sorted)
    
    historical_data_with_averages = {
        'symbol': symbol,
        'data': last_10_days_data,
        'current_price': current_price,
        'two_week_average': two_week_average
    }

    return historical_data_with_averages




@app.route('/', methods=['GET', 'POST'])
def index():
    stock_data_list = []
    historical_data = None
    search_symbol = None  # Initialize the variable

    
    # reload the first page of the flask to get all stock deaily data

    if request.method == 'POST':
        if 'reload' in request.form:
            # Reload all stocks
            for symbol in available_stocks:

                ###################################################
                try:
                    # read data from MongoDB Compass 
                    onlineStockDailyData = myStockDBDaily.find_one({"symbol": symbol})  # read daily data
                    if onlineStockDailyData:
                        # put daily data into list
                        stock_data_list.append(onlineStockDailyData)
                    else:
                        break

                except AlphaVantageApiException as e:
                    print(e)
                ###################################################

        else:
            # Search for specific stock symbol
            search_symbol = request.form.get('search_symbol').upper()
            if search_symbol in available_stocks:
                try:

                    ###################################################
                    # Fetch historical data for the specific stock symbol
                    historical_data = myStockDB2Week.find_one({"symbol": search_symbol})    # from MongoDB Compass data
                    ###################################################

                except AlphaVantageApiException as e:
                    print(e)

        return render_template('index.html', stock_data_list=stock_data_list, historical_data=historical_data, symbol=search_symbol)

    else:
        # Initial page load with all stocks
        for symbol in available_stocks:

          
            ###################################################
            # uncomment these codes if it is 
            # using "try" function to check the stock data available or not,
            # and store them into the MongoDB Compass
            try:
                stock_data = get_stock_data(symbol)
                if stock_data:
                    #################################
                    # store the stock data into MongoDB Compass
                    x = myStockDB2Week.insert_one(get_historical_stock_data(symbol))    # store 2 week data
                    y = myStockDBDaily.insert_one(get_stock_data(symbol))   # store daily data
                    #################################
                else:
                    break

            except AlphaVantageApiException as e:
                print(e)
            ###################################################
          
            
            ###################################################
            try:
                # read data from MongoDB Compass 
                onlineStockDailyData = myStockDBDaily.find_one({"symbol": symbol})  # read daily data
                if onlineStockDailyData:
                    # put daily data into list
                    stock_data_list.append(onlineStockDailyData)
                else:
                    break

            except AlphaVantageApiException as e:
                print(e) 
            ###################################################
 

    return render_template('index.html', stock_data_list=stock_data_list)



@app.errorhandler(AlphaVantageApiException)
def handle_api_error(error):
    # Here you would define what to do when an AlphaVantageApiException is raised
    # For the purpose of this example, let's just pass the message to an error template.
    return render_template('error.html', message=error), 500



if __name__ == '__main__':
    app.run(debug=True)