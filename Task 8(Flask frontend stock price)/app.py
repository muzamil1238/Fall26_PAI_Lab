from flask import Flask, render_template, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/stock/<symbol>")
def get_stock_price(symbol):
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol.upper(),
        "apikey": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Global Quote" not in data or not data["Global Quote"]:
        return jsonify({"error": "Invalid symbol or API limit reached"}), 400

    stock_data = data["Global Quote"]

    result = {
        "symbol": stock_data["01. symbol"],
        "price": stock_data["05. price"],
        "change": stock_data["09. change"],
        "change_percent": stock_data["10. change percent"],
        "volume": stock_data["06. volume"],
        "previous_close": stock_data["08. previous close"]
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)