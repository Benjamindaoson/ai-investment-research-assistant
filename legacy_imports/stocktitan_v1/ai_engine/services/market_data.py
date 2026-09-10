import yfinance as yf
import pandas as pd
from typing import List, Dict
import logging

def get_market_overview() -> Dict:
    """
    Fetches a snapshot of key indices and hot stocks for US, A-Share, and HK markets.
    """
    # Define indices to watch
    # yfinance symbol formats: ^GSPC (S&P 500), 000001.SS (SSE Composite), ^HSI (Hang Seng)
    idx_map = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Dow Jones": "^DJI",
        "上证指数": "000001.SS",
        "深证成指": "399001.SZ",
        "恒生指数": "^HSI"
    }
    
    indices = []
    try:
        # Fetch indices
        for name, sym in idx_map.items():
            t = yf.Ticker(sym)
            # Use history for more reliable 'last' and 'prev close' than fast_info
            hist = t.history(period="2d")
            if len(hist) >= 2:
                last_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
            elif len(hist) == 1:
                last_price = hist['Close'].iloc[-1]
                prev_close = last_price # Fallback
            else:
                last_price = 0
                prev_close = 0
                
            change = last_price - prev_close
            pct_change = (change / prev_close * 100) if prev_close != 0 else 0
            
            indices.append({
                "name": name,
                "symbol": sym,
                "price": round(last_price, 2),
                "change": round(change, 2),
                "pct_change": round(pct_change, 2)
            })
    except Exception as e:
        logging.error(f"Error fetching indices: {e}")

    # Hot stocks
    hot_stocks = {
        "US": ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL"],
        "CN": ["600519.SS", "000858.SZ", "601318.SS", "002594.SZ", "300750.SZ"],
        "HK": ["0700.HK", "9988.HK", "3690.HK", "1211.HK", "2318.HK"]
    }
    
    market_lists = {}
    for market, syms in hot_stocks.items():
        list_data = []
        try:
            for s in syms:
                t = yf.Ticker(s)
                hist = t.history(period="2d")
                if len(hist) >= 2:
                    p = hist['Close'].iloc[-1]
                    pc = hist['Close'].iloc[-2]
                elif len(hist) == 1:
                    p = hist['Close'].iloc[-1]
                    pc = p
                else:
                    p = 0
                    pc = 0
                ch = p - pc
                pch = (ch / pc * 100) if pc != 0 else 0
                list_data.append({
                    "symbol": s,
                    "price": round(p, 2),
                    "pct_change": round(pch, 2)
                })
        except Exception as e:
            logging.error(f"Error fetching {market} stocks: {e}")
        market_lists[market] = list_data

    return {
        "indices": indices,
        "lists": market_lists
    }
