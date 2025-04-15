
from flask import Flask, request, jsonify
from tradingview_ta import TA_Handler, Interval
import os

app = Flask(__name__)

interval_map = {
    "1m": Interval.INTERVAL_1_MINUTE,
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY,
    "1w": Interval.INTERVAL_1_WEEK,
    "1M": Interval.INTERVAL_1_MONTH
}

def get_analysis(symbol, exchange, screener, interval):
    handler = TA_Handler(
        symbol=symbol,
        exchange=exchange,
        screener=screener,
        interval=interval
    )
    analysis = handler.get_analysis()
    return {
        "symbol": symbol,
        "exchange": exchange,
        "screener": screener,
        "interval": interval,
        "recommendation": analysis.summary["RECOMMENDATION"],
        "score": analysis.summary
    }

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        symbol = data.get("symbol")
        exchange = data.get("exchange")
        screener = data.get("screener")
        interval_key = data.get("interval")

        if not all([symbol, exchange, screener, interval_key]):
            return jsonify({"error": "Missing input fields"}), 400

        if interval_key not in interval_map:
            return jsonify({"error": f"Invalid interval: {interval_key}"}), 400

        result = get_analysis(symbol, exchange, screener, interval_map[interval_key])
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "✅ Dan's TradingView AI API is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
