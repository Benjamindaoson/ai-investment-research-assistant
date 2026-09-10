import pandas as pd
import numpy as np
import yfinance as yf
from typing import List
from models.schemas import SignalRecord, BacktestResult
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def evaluate_signals_batch(signals: List[SignalRecord]) -> BacktestResult:
    """
    Takes a batch of SignalRecords, downloads real historical execution data using yfinance,
    and performs exact quantitative vectorized backtesting computation.
    """
    if not signals:
        return BacktestResult(
            total_signals=0, hit_rate_pct=0.0, avg_return_pct=0.0,
            status="RETIRED", weight=0.0
        )
        
    df = pd.DataFrame([s.dict() for s in signals])
    symbols = df['symbol'].unique().tolist()
    
    # Clean timestamp context
    df['created_datetime'] = pd.to_datetime(df['created_at'].astype(int), unit='s')
    df['target_date_t20'] = df['created_datetime'] + pd.Timedelta(days=20)
    
    # Find the earliest and latest dates we need context for
    min_date = df['created_datetime'].min().strftime('%Y-%m-%d')
    max_date = (df['target_date_t20'].max() + pd.Timedelta(days=5)).strftime('%Y-%m-%d')
    
    logger.info(f"Downloading yfinance history for {len(symbols)} symbols from {min_date} to {max_date}")
    
    # Bulk fetch real data
    try:
        yf_data = yf.download(symbols, start=min_date, end=max_date, period="1d", group_by="ticker", auto_adjust=True, progress=False)
    except Exception as e:
        logger.error(f"Failed to fetch yfinance data: {e}")
        # Return graceful failure
        return BacktestResult(total_signals=len(signals), hit_rate_pct=0.0, avg_return_pct=0.0, status="ERROR", weight=0.0)

    # Resolve target prices
    actual_returns = []
    is_hits = []
    
    for idx, row in df.iterrows():
        sym = row['symbol']
        entry_price = float(row['entry_price'])
        created_dt = row['created_datetime']
        target_dt = row['target_date_t20']
        direction = str(row['direction']).upper()
        
        # Extract stock history
        try:
            if len(symbols) == 1:
                hist = yf_data
            else:
                hist = yf_data[sym]
                
            # Filter history to dates after creation
            future_hist = hist[hist.index >= pd.to_datetime(created_dt.date())]
            
            if future_hist.empty:
                # No future data (happened today or weekend)
                actual_returns.append(0.0)
                is_hits.append(False)
                continue
            
            # Find the closing price right at or after target date (T+20)
            target_mask = future_hist.index >= pd.to_datetime(target_dt.date())
            if not target_mask.any():
                # If target date hasn't arrived, take the latest available
                target_price = float(future_hist['Close'].iloc[-1])
            else:
                target_price = float(future_hist[target_mask]['Close'].iloc[0])
                
            if entry_price > 0:
                ret_pct = ((target_price - entry_price) / entry_price) * 100
            else:
                ret_pct = 0.0
                
            # Hit logic
            if direction == "BULLISH":
                hit = ret_pct > 0
            elif direction == "BEARISH":
                hit = ret_pct < 0
            else:
                hit = abs(ret_pct) <= 2.0
                
            actual_returns.append(ret_pct)
            is_hits.append(hit)
            
        except Exception as e:
            logger.debug(f"Missing data for {sym} at {created_dt}: {e}")
            actual_returns.append(0.0)
            is_hits.append(False)
            
    df['real_return'] = actual_returns
    df['is_hit'] = is_hits
    
    total_signals = len(df)
    hits = df['is_hit'].sum()
    hit_rate = (hits / total_signals) * 100 if total_signals > 0 else 0.0
    avg_return = df['real_return'].mean()
    
    # Strategy Governance Rule Engine
    status = "ACTIVE"
    weight = 1.0
    
    if total_signals >= 20 and hit_rate < 45.0:
        status = "RETIRED"
        weight = 0.0
    elif total_signals >= 10 and hit_rate < 52.0:
        status = "DOWNWEIGHT"
        weight = 0.5
        
    logger.info(f"Backtest REAL complete: {total_signals} signals, {hit_rate:.2f}% hit rate. Governance: {status}")
    
    return BacktestResult(
        total_signals=total_signals,
        hit_rate_pct=round(float(hit_rate), 2),
        avg_return_pct=round(float(avg_return), 2),
        status=status,
        weight=float(weight)
    )
