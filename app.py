

from flask import Flask, render_template
from repos.stock_api import get_stock_data  # Import the get_stock_data function
from repos.exceptions import AlphaVantageApiException

app = Flask(__name__)

available_stocks = ["PTON", "GME", "COIN", "ZM", "BYND", "AMC", "RBLX", "AAPL", "AMZN", "NVDA", "ACB", "SHOP", "NFLX", "DIS", "GOOG", "TSLA", "META", "MSFT"]

@app.route('/', methods=['GET'])
def index():
    stock_data_list = []
    for symbol in available_stocks:
        try:
            stock_data = get_stock_data(symbol)
            if stock_data is not None:
                stock_data_list.append(stock_data)
        except AlphaVantageApiException as e:
            print(e)
            continue
    return render_template('index.html', stock_data_list=stock_data_list)

@app.errorhandler(AlphaVantageApiException)
def handle_api_error(error):
    return render_template('error.html', message=error), 500

if __name__ == '__main__':
    app.run(debug=True)
