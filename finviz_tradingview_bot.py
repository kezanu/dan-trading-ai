import requests
from tradingview_ta import TA_Handler, Interval
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
import re

WEBHOOK_URL = "https://hook.eu2.make.com/14ub8oo8d3wj64stedeo6k8kxeqshs21"
INTERVAL = Interval.INTERVAL_1_HOUR

TICKERS_FIXE = [
    {"symbol": "DIA", "exchange": "AMEX", "screener": "america"},
    {"symbol": "XAUUSD", "exchange": "FOREXCOM", "screener": "forex"},
    {"symbol": "EURUSD", "exchange": "OANDA", "screener": "forex"},
    {"symbol": "GBPJPY", "exchange": "OANDA", "screener": "forex"},
    {"symbol": "USDCAD", "exchange": "OANDA", "screener": "forex"},
    {"symbol": "CHFCAD", "exchange": "OANDA", "screener": "forex"},
    {"symbol": "GBPCHF", "exchange": "OANDA", "screener": "forex"}
]

def get_finviz_tickers():
    url = "https://finviz.com/screener.ashx?v=111&f=cap_micro,geo_usa,sh_float_u50,sh_price_u10,ta_perf_prevup5&o=-change"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')

    tickers = []
    for link in soup.find_all('a', href=True):
        if link['href'].startswith("quote.ashx"):
            ticker = link.text.strip()
            if re.match(r'^[A-Z]{1,5}$', ticker):
                tickers.append({
                    "symbol": ticker,
                    "exchange": "NASDAQ",
                    "screener": "america"
                })
    return tickers[:10]

def analyze_ticker(ticker):
    try:
        handler = TA_Handler(
            symbol=ticker['symbol'],
            exchange=ticker['exchange'],
            screener=ticker['screener'],
            interval=INTERVAL
        )
        analysis = handler.get_analysis()
        indicators = analysis.indicators
        summary = analysis.summary

        rsi = indicators.get('RSI', 'N/A')
        macd = indicators.get('MACD.macd', 'N/A')
        ema = indicators.get('EMA20', 'N/A')
        recomandare = summary['RECOMMENDATION']
        scor = (list(summary.values()).count("BUY") - list(summary.values()).count("SELL")) * 10 + 50
        tp = sl = price = indicators['close']

        if recomandare in ["BUY", "STRONG_BUY"]:
            tp *= 1.02
            sl *= 0.99
        elif recomandare in ["SELL", "STRONG_SELL"]:
            tp *= 0.98
            sl *= 1.01

        return {
            "ticker": ticker['symbol'],
            "tip_piata": "Forex" if ticker['screener'] == "forex" else "Stock",
            "recomandare": recomandare,
            "tp": round(tp, 2),
            "sl": round(sl, 2),
            "rsi": round(rsi, 2) if isinstance(rsi, (int, float)) else rsi,
            "macd": round(macd, 2) if isinstance(macd, (int, float)) else macd,
            "ema": round(ema, 2) if isinstance(ema, (int, float)) else ema,
            "scor": scor,
            "comentarii": f"RSI: {rsi} | MACD: {macd} | EMA: {ema}",
            "link": f"https://www.tradingview.com/symbols/{ticker['symbol']}/",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Eroare analiză {ticker['symbol']}: {e}")
        return None

def trimite_webhook(payload):
    try:
        r = requests.post(WEBHOOK_URL, json=payload)
        print(f"✅ Trimis: {payload['ticker']} | Scor: {payload['scor']}")
    except Exception as e:
        print(f"Eșec trimitere {payload['ticker']}: {e}")

if __name__ == "__main__":
    print("Start analiză la:", datetime.now())
    tickere = TICKERS_FIXE + get_finviz_tickers()
    for t in tickere:
        if t['symbol'].lower() not in ["usa"]:
            rezultat = analyze_ticker(t)
            if rezultat:
                trimite_webhook(rezultat)
    print("✅ Toate alertele au fost procesate!")
