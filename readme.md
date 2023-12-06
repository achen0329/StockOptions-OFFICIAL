    
   StockPulse is the premier stock price application for all your investment needs designed to deliver both current and historical stock data. StockPulse provides a a delightful end user experince through its cutting-edge SPA design fully integrated with the Alpha Vantage API and a DB connection for lightning fast response times. Users will be equipped with the current and historical stock market data they need to make informed financial decisions. Here's how to get started (below).

![Alt text](<app_screenshots/StockOptions - OFFICIAL Home.png> "Initial App Rendering")




![Alt text](<app_screenshots/StockOptions - OFFICIAL Search.png> "Search Results")





    From a Windows operating system one can download the repository and follow the following steps to get started:

    1. py -3 -m venv env
    2. env\scripts\activate
    3. python -m pip install -r requirements.txt
    4. flask run

    Once a user initializes a virtual environment for the project, they will need to activate it. Within this virtual environment the dependencies for the project will be installed and a user can then run the flask application.

    In addition a user will need to register for a free API key at Alpha Vantage's website to enable the API integrations: https://www.alphavantage.co/support/#api-key

    Future work for the project includes cloud deployment for scaling the product and implementing CI/CD processes for automatic database updates.