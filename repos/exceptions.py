class AlphaVantageApiException(Exception):
    def __init__(self, status_code):
        if status_code == 403:
            message = "Rate limit reached. Please wait a minute and try again."
        elif status_code == 503:
            message = "Service unavailable. Please try again later."
        else:
            message = f"HTTP Status Code was: {status_code}."

        super().__init__("An Alpha Vantage API Error Occurred: " + message)
