from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Stock Price API",
        "usage": "/stock/<symbol>"
    })

@app.route("/stock/<symbol>")
def get_stock_price(symbol):
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Global Quote" not in data:
        return jsonify({"error": "Invalid symbol or API limit reached"}), 400

    stock_data = data["Global Quote"]

    result = {
        "symbol": stock_data["01. symbol"],
        "open": stock_data["02. open"],
        "high": stock_data["03. high"],
        "low": stock_data["04. low"],
        "price": stock_data["05. price"],
        "volume": stock_data["06. volume"],
        "latest_trading_day": stock_data["07. latest trading day"],
        "previous_close": stock_data["08. previous close"],
        "change": stock_data["09. change"],
        "change_percent": stock_data["10. change percent"]
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)