import streamlit as st
import requests
import pandas as pd
import json
import time
import random
from datetime import datetime, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="StockTitan AI Engine",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PREMIUM CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1627 50%, #111827 100%);
        color: #e2e8f0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1629 0%, #141e30 100%) !important;
        border-right: 1px solid rgba(79, 172, 254, 0.15) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] p {
        color: #94a3b8 !important;
    }
    
    /* Hero Header */
    .hero-header {
        background: linear-gradient(135deg, rgba(79,172,254,0.08) 0%, rgba(0,242,254,0.04) 100%);
        border: 1px solid rgba(79,172,254,0.2);
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 32px;
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(79,172,254,0.1) 0%, transparent 70%);
    }
    
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 8px 0;
    }
    
    .hero-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(79,172,254,0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(79,172,254,0.35);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #4facfe;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .badge-active { background: rgba(16,185,129,0.2); color: #10b981; border: 1px solid rgba(16,185,129,0.4); }
    .badge-retired { background: rgba(239,68,68,0.2); color: #ef4444; border: 1px solid rgba(239,68,68,0.4); }
    .badge-downweight { background: rgba(245,158,11,0.2); color: #f59e0b; border: 1px solid rgba(245,158,11,0.4); }
    
    /* Metrics */
    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
    .metric-card {
        background: rgba(79,172,254,0.06);
        border: 1px solid rgba(79,172,254,0.15);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #4facfe; }
    .metric-label { font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px; }
    .metric-delta-pos { color: #10b981; font-size: 0.82rem; }
    .metric-delta-neg { color: #ef4444; font-size: 0.82rem; }
    
    /* Agent timeline */
    .agent-step {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        padding: 16px 0;
        border-bottom: 1px solid rgba(79,172,254,0.08);
    }
    .agent-icon {
        width: 44px; height: 44px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }
    .icon-analyst { background: rgba(79,172,254,0.15); }
    .icon-risk { background: rgba(239,68,68,0.15); }
    .icon-advisor { background: rgba(16,185,129,0.15); }
    .agent-content { flex: 1; }
    .agent-name { font-weight: 600; font-size: 0.88rem; color: #cbd5e1; margin-bottom: 4px; }
    .agent-text { font-size: 0.83rem; color: #64748b; line-height: 1.55; }
    
    /* Decision box */
    .decision-box {
        background: linear-gradient(135deg, rgba(79,172,254,0.12) 0%, rgba(0,242,254,0.06) 100%);
        border: 1.5px solid rgba(79,172,254,0.35);
        border-radius: 14px;
        padding: 24px;
        margin-top: 20px;
        text-align: center;
    }
    .decision-advice {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .advice-buy { color: #10b981; }
    .advice-sell { color: #ef4444; }
    .advice-hold { color: #f59e0b; }
    
    /* Progress bar custom */
    .progress-container { margin: 8px 0; }
    .progress-label { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.8rem; color: #94a3b8; }
    .progress-bar-bg {
        height: 8px;
        background: rgba(255,255,255,0.06);
        border-radius: 4px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #4facfe, #00f2fe);
        transition: width 0.6s ease;
    }
    
    /* Table */
    .data-table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    .data-table th {
        padding: 10px 14px;
        text-align: left;
        font-size: 0.72rem;
        font-weight: 600;
        color: #4facfe;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-bottom: 1px solid rgba(79,172,254,0.2);
    }
    .data-table td {
        padding: 12px 14px;
        font-size: 0.84rem;
        color: #cbd5e1;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .data-table tr:hover td { background: rgba(79,172,254,0.04); }
    
    /* Stremlit default overrides */
    .stButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00c2fe 100%);
        color: #0a0e1a;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 700;
        font-size: 0.9rem;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(79,172,254,0.4);
    }
    
    div[data-testid="metric-container"] {
        background: rgba(79,172,254,0.05);
        border: 1px solid rgba(79,172,254,0.15);
        border-radius: 12px;
        padding: 16px;
    }
    
    div[data-testid="metric-container"] label {
        color: #64748b !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: #4facfe !important;
        font-weight: 700 !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div {
        background: rgba(6,11,22,0.8) !important;
        border: 1px solid rgba(79,172,254,0.2) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: rgba(79,172,254,0.6) !important;
        box-shadow: 0 0 0 2px rgba(79,172,254,0.15) !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        color: #4facfe;
    }
    
    div.stAlert {
        background: rgba(79,172,254,0.08) !important;
        border: 1px solid rgba(79,172,254,0.25) !important;
        border-radius: 12px !important;
        color: #94a3b8 !important;
    }
    
    h3 { color: #e2e8f0 !important; }
    
    .stCheckbox label span { color: #94a3b8 !important; }
    .stCheckbox [data-baseweb="checkbox"] div { border-color: rgba(79,172,254,0.4) !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONFIG
# ============================================================
FASTAPI_URL = "http://127.0.0.1:8000"

def check_server():
    try:
        r = requests.get(f"{FASTAPI_URL}/health", timeout=2)
        return r.status_code == 200
    except:
        return False

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 10px 0;">
        <div style="font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            📈 StockTitan
        </div>
        <div style="font-size: 0.75rem; color: #475569; margin-top: 4px;">AI Engine Control Panel</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Server status
    alive = check_server()
    status_color = "#10b981" if alive else "#ef4444"
    status_text = "● Online" if alive else "● Offline"
    st.markdown(f"""
    <div style="font-size: 0.8rem; color: {status_color}; margin-bottom: 16px;">
        {status_text} &nbsp;—&nbsp; <span style="color: #475569;">FastAPI Engine</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox(
        "Navigation",
        ["🤖 Multi-Agent Analyst", "📊 Quant Backtest Engine", "🔍 RAG Reranker", "📡 System Diagnostics"]
    )

    st.divider()
    st.markdown('<div style="font-size: 0.72rem; color: #334155;">Architecture</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.78rem; color: #475569; line-height: 1.8;">
        🔷 Java Gateway (Spring Boot)<br>
        ↓ HTTP REST Bridge<br>
        🐍 Python AI Engine<br>
        &nbsp;&nbsp;├ LangGraph StateGraph<br>
        &nbsp;&nbsp;├ Pandas Backtester<br>
        &nbsp;&nbsp;└ CrossEncoder Reranker
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero-header">
    <div class="hero-title">StockTitan AI Engine</div>
    <div class="hero-subtitle">Dual-Engine Architecture &nbsp;·&nbsp; Java Spring Boot Gateway &nbsp;+&nbsp; Python AI Microservice (LangGraph · Pandas · HuggingFace)</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PAGE: MULTI-AGENT ANALYST
# ============================================================
if page == "🤖 Multi-Agent Analyst":
    st.markdown("### 🤖 Multi-Agent Orchestration — LangGraph StateGraph")
    st.markdown('<div style="color:#475569;font-size:0.88rem;margin:-12px 0 24px 0;">Chains `DataFetcher → Analyst → RiskManager → Advisor` via LangGraph. Each agent receives enriched yfinance context.</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.2], gap="large")

    with col_left:
        st.markdown('<div class="card-title">⚙️ Configuration</div>', unsafe_allow_html=True)
        stock_code = st.text_input("Stock Symbol", value="AAPL", placeholder="e.g. AAPL, TSLA, NVDA")
        price = st.number_input("Reference Price (USD)", value=185.50, step=0.01)
        news_input = st.text_area(
            "Latest News / Event",
            value="Apple reported Q1 FY2025 earnings beating estimates by 8%, with strong iPhone 16 Pro sales and Services revenue up 14% YoY.",
            height=120
        )
        include_context = st.checkbox("Enrich with live yfinance market data", value=True)

        run_btn = st.button("▶  Run Agent Chain", key="run_agents")

    with col_right:
        if run_btn:
            if not alive:
                st.error("❌ FastAPI server is not running. Please start `launch_api.bat` first.")
            else:
                with st.spinner(""):
                    # Agent progress animation
                    agents = [
                        ("📡", "DataFetcher", "icon-analyst", "Pulling live yfinance data — market cap, PE, 52w range..."),
                        ("🔬", "Analyst", "icon-analyst", "Synthesizing investment thesis and catalysts..."),
                        ("⚠️", "Risk Manager", "icon-risk", "Scanning macro/micro risk exposure..."),
                        ("🎯", "Advisor", "icon-advisor", "Formulating final structured decision..."),
                    ]
                    
                    progress_placeholder = st.empty()
                    for i, (icon, name, cls, desc) in enumerate(agents):
                        with progress_placeholder.container():
                            st.markdown(f'<div class="card-title">🔄 Agent Pipeline Running...</div>', unsafe_allow_html=True)
                            for j, (ic, n, c, d) in enumerate(agents):
                                if j < i:
                                    st.markdown(f'<div class="agent-step"><div class="agent-icon {c}" style="opacity:0.5">{ic}</div><div class="agent-content"><div class="agent-name" style="color:#4facfe">✓ {n}</div><div class="agent-text" style="color:#334155">{d}</div></div></div>', unsafe_allow_html=True)
                                elif j == i:
                                    st.markdown(f'<div class="agent-step"><div class="agent-icon {c}">{ic}</div><div class="agent-content"><div class="agent-name">{n} (running...)</div><div class="agent-text">{d}</div></div></div>', unsafe_allow_html=True)
                        time.sleep(0.8)
                    
                    progress_placeholder.empty()

                    payload = {
                        "stock_code": stock_code.upper().strip(),
                        "price": price,
                        "news": [news_input]
                    }
                    
                    try:
                        resp = requests.post(f"{FASTAPI_URL}/api/v1/orchestrate", json=payload, timeout=120)
                        if resp.status_code == 200:
                            data = resp.json()
                            
                            advice = data.get("advice", "HOLD").upper()
                            advice_class = {"BUY": "advice-buy", "SELL": "advice-sell"}.get(advice, "advice-hold")
                            conf = data.get("confidence", 0)

                            # Agent outputs display
                            st.markdown('<div class="card-title">🔄 Agent Execution Trace</div>', unsafe_allow_html=True)
                            steps = [
                                ("📡", "DataFetcher Agent", "icon-analyst", f"Retrieved live market context for {stock_code.upper()} via yfinance"),
                                ("🔬", "Analyst Agent", "icon-analyst", data.get("executive_summary", "")[:280] + "..."),
                                ("⚠️", "Risk Manager Agent", "icon-risk", "; ".join(data.get("risk_factors", [])[:2])),
                                ("🎯", "Advisor Agent", "icon-advisor", data.get("conclusion", "")[:200]),
                            ]
                            for icon, name, cls, text in steps:
                                st.markdown(f'<div class="agent-step"><div class="agent-icon {cls}">{icon}</div><div class="agent-content"><div class="agent-name">{name}</div><div class="agent-text">{text}</div></div></div>', unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="decision-box">
                                <div style="font-size:0.78rem;color:#475569;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Final Investment Decision</div>
                                <div class="decision-advice {advice_class}">{advice}</div>
                                <div style="color:#4facfe;font-size:1.1rem;font-weight:600;">Confidence: {conf}%</div>
                            </div>
                            """, unsafe_allow_html=True)

                        else:
                            st.error(f"API Error {resp.status_code}: {resp.text[:300]}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:60px 24px;">
                <div style="font-size:3rem;margin-bottom:16px;">🤖</div>
                <div style="color:#475569;font-size:0.9rem;">Configure parameters and run the Agent Chain to see the LangGraph execution trace and final investment decision.</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# PAGE: QUANT BACKTEST
# ============================================================
elif page == "📊 Quant Backtest Engine":
    st.markdown("### 📊 Pandas Vectorized T+N Backtest Engine")
    st.markdown('<div style="color:#475569;font-size:0.88rem;margin:-12px 0 24px 0;">Evaluates batches of AI trading signals against real Yahoo Finance historical data. Vectorized via Pandas for massive throughput.</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1.5], gap="large")

    with col_l:
        st.markdown('<div class="card-title">⚙️ Backtest Parameters</div>', unsafe_allow_html=True)
        
        symbol = st.selectbox("Stock Symbol", ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL"])
        direction = st.selectbox("Signal Direction", ["BULLISH", "BEARISH", "NEUTRAL"])
        num_signals = st.slider("Number of Signals", min_value=5, max_value=500, value=30)
        entry_price = st.number_input("Entry Price (USD)", value=180.0, step=0.5)
        
        run_backtest_btn = st.button("▶  Run Vectorized Backtest", key="run_backtest")

    with col_r:
        if run_backtest_btn:
            if not alive:
                st.error("❌ FastAPI server is not running. Please start `launch_api.bat` first.")
            else:
                with st.spinner(f"Fetching {symbol} historical data via yfinance and vectorizing {num_signals} signals..."):
                    # Build payload with distributed timestamps over last 6 months
                    now_ts = int(datetime.now().timestamp())
                    payload = []
                    for i in range(num_signals):
                        offset_days = random.randint(0, 180)
                        ts = now_ts - (offset_days * 86400)
                        payload.append({
                            "id": f"sig-{i:04d}",
                            "symbol": symbol,
                            "direction": direction,
                            "entry_price": entry_price + random.uniform(-5, 5),
                            "confidence": random.randint(45, 90),
                            "created_at": str(ts)
                        })
                    
                    try:
                        resp = requests.post(f"{FASTAPI_URL}/api/v1/backtest", json=payload, timeout=120)
                        if resp.status_code == 200:
                            data = resp.json()
                            hit = data["hit_rate_pct"]
                            ret = data["avg_return_pct"]
                            total = data["total_signals"]
                            status = data["status"]
                            weight = data["weight"]
                            
                            badge_class = {"ACTIVE": "badge-active", "RETIRED": "badge-retired", "DOWNWEIGHT": "badge-downweight"}.get(status, "badge-active")
                            
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Hit Rate", f"{hit:.1f}%", delta=f"{'▲' if hit > 50 else '▼'} {'Above' if hit > 50 else 'Below'} 50%")
                            c2.metric("Avg Return (T+20)", f"{ret:.2f}%", delta="Vectorized via Pandas")
                            c3.metric("Total Signals", str(total), delta=f"Weight: {weight:.1f}x")
                            
                            st.markdown(f"""
                            <div class="glass-card" style="margin-top:16px;">
                                <div class="card-title">📋 Strategy Governance Decision</div>
                                <div style="margin-top:4px;">
                                    <span class="status-badge {badge_class}">{status}</span>
                                    <span style="color:#64748b;font-size:0.82rem;margin-left:12px;">Strategy weight: <b style="color:#e2e8f0">{weight:.1f}x</b></span>
                                </div>
                                <div style="margin-top:16px;font-size:0.82rem;color:#64748b;">
                                    {"✅ This strategy meets the minimum hit rate threshold (≥52%) — fully active." if status == "ACTIVE" else
                                     "⚠️ Hit rate between 45–52% with 10+ samples → down-weighted to 0.5x position size." if status == "DOWNWEIGHT" else
                                     "❌ Hit rate below 45% across 20+ validated signals → strategy retired automatically."}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Signal sample table
                            st.markdown('<div class="card-title" style="margin-top:8px;">📝 Signal Sample (first 10)</div>', unsafe_allow_html=True)
                            sample_df = pd.DataFrame(payload[:10])[["id", "symbol", "direction", "entry_price", "confidence"]]
                            sample_df.columns = ["Signal ID", "Symbol", "Direction", "Entry $", "Confidence"]
                            st.dataframe(sample_df, use_container_width=True)

                        else:
                            st.error(f"API Error {resp.status_code}: {resp.text}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:60px 24px;">
                <div style="font-size:3rem;margin-bottom:16px;">📊</div>
                <div style="color:#475569;font-size:0.9rem;">Configure your signal parameters and run the backtest. The Python engine will download real historical prices from Yahoo Finance and evaluate each signal against actual market outcomes.</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# PAGE: RAG RERANKER
# ============================================================
elif page == "🔍 RAG Reranker":
    st.markdown("### 🔍 Hybrid RAG with Deep Learning Reranker")
    st.markdown('<div style="color:#475569;font-size:0.88rem;margin:-12px 0 24px 0;">Simulates the full RAG pipeline: vector recall (cosine) → quality filter → CrossEncoder neural reranking via `cross-encoder/ms-marco-MiniLM-L-6-v2`.</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1.3], gap="large")

    with col_l:
        st.markdown('<div class="card-title">⚙️ Query Configuration</div>', unsafe_allow_html=True)
        query = st.text_area("User Query / Event Description", value="Apple beats earnings expectations with strong iPhone sales and raised guidance", height=100)
        top_k = st.slider("Top K after reranking", 1, 5, 3)
        
        st.markdown('<div class="card-title" style="margin-top:20px;">📚 Candidate Corpus (simulated vector recall)</div>', unsafe_allow_html=True)
        
        # Pre-loaded candidates for demo
        default_candidates = [
            {"id": "c001", "stock_code": "AAPL", "title": "Apple Q3 2024 Earnings Beat", "description": "Apple exceeded analyst estimates by 7% with strong iPhone 15 Pro cycle.", "analysis": "iPhone sales drove outperformance; services segment continues double-digit growth.", "actual_impact": "Stock surged 5.2% next session", "occurred_at": "2024-08-01"},
            {"id": "c002", "stock_code": "AAPL", "title": "Apple iPhone Supply Constraint Warning", "description": "Analyst downgrades amid potential component shortage concerns for Q4.", "analysis": "Supply chain disruptions from Asia could limit holiday quarter upside.", "actual_impact": "Stock fell 3.1% on the day", "occurred_at": "2023-11-15"},
            {"id": "c003", "stock_code": "MSFT", "title": "Microsoft Azure Cloud Revenue Acceleration", "description": "Azure grew 28% YoY, beating estimates as AI workloads proliferate.", "analysis": "Copilot integration driving enterprise adoption and premium pricing power.", "actual_impact": "Stock gained 4.8% post-earnings", "occurred_at": "2024-10-30"},
            {"id": "c004", "stock_code": "AAPL", "title": "Apple Services Record Revenue Quarter", "description": "App Store, iCloud, and Apple TV+ collectively hit $24.2B in a single quarter.", "analysis": "High-margin services segment diversifying revenue beyond hardware cycles.", "actual_impact": "Stock up 2.9% month over month", "occurred_at": "2024-05-02"},
            {"id": "c005", "stock_code": "GOOGL", "title": "Alphabet Advertising Revenue Miss", "description": "Display and search ad revenue disappointed amid macro headwinds.", "analysis": "Competition from TikTok and Amazon ads eroding Google's market share.", "actual_impact": "Stock fell 6.1% over two sessions", "occurred_at": "2024-07-25"},
        ]
        
        num_candidates = st.slider("Number of vector recall candidates", 2, 5, 5)
        run_rerank_btn = st.button("▶  Run Cross-Encoder Reranking", key="run_rerank")

    with col_r:
        if run_rerank_btn:
            if not alive:
                st.error("❌ FastAPI server is not running. Please start `launch_api.bat` first.")
            else:
                candidates = default_candidates[:num_candidates]
                
                with st.spinner("Running CrossEncoder model (ms-marco-MiniLM-L-6-v2)..."):
                    payload = {
                        "query": query,
                        "candidates": candidates,
                        "top_k": top_k
                    }
                    
                    try:
                        resp = requests.post(f"{FASTAPI_URL}/api/v1/rerank", json=payload, timeout=60)
                        if resp.status_code == 200:
                            reranked = resp.json()
                            
                            # Before
                            st.markdown('<div class="card-title">📋 Before Reranking (Raw Vector Recall Order)</div>', unsafe_allow_html=True)
                            st.markdown('<table class="data-table"><tr><th>#</th><th>Stock</th><th>Title</th><th>Actual Impact</th></tr>' + 
                                "".join(f"<tr><td>{i+1}</td><td>{c['stock_code']}</td><td>{c['title']}</td><td>{c.get('actual_impact','—')}</td></tr>" for i, c in enumerate(candidates)) +
                                "</table>", unsafe_allow_html=True)
                            
                            st.divider()
                            
                            # After
                            st.markdown('<div class="card-title">🏆 After CrossEncoder Reranking (Top K Most Relevant)</div>', unsafe_allow_html=True)
                            for i, case in enumerate(reranked):
                                gold = i == 0
                                border_color = "rgba(79,172,254,0.5)" if gold else "rgba(79,172,254,0.15)"
                                st.markdown(f"""
                                <div class="glass-card" style="border-color:{border_color};margin-bottom:12px;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                                        <div style="font-weight:600;color:#e2e8f0;">{'🥇' if gold else f'#{i+1}'} &nbsp;{case['stock_code']} — {case['title']}</div>
                                        <span class="status-badge badge-active" style="font-size:0.7rem;">Rank {i+1}</span>
                                    </div>
                                    <div style="font-size:0.82rem;color:#64748b;">{case['analysis']}</div>
                                    <div style="font-size:0.78rem;color:#4facfe;margin-top:6px;">📌 {case.get('actual_impact','—')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error(f"API Error {resp.status_code}: {resp.text}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:60px 24px;">
                <div style="font-size:3rem;margin-bottom:16px;">🔍</div>
                <div style="color:#475569;font-size:0.9rem;">The Reranker sends candidate documents to the Python CrossEncoder model which computes exact semantic relevance scores, dramatically improving RAG precision over cosine similarity alone.</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# PAGE: DIAGNOSTICS
# ============================================================
elif page == "📡 System Diagnostics":
    st.markdown("### 📡 System Diagnostics")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### API Endpoints Health")
        endpoints = [
            ("/health", "GET", "Health Check"),
            ("/api/v1/orchestrate", "POST", "LangGraph Orchestrator"),
            ("/api/v1/backtest", "POST", "Pandas Backtester"),
            ("/api/v1/rerank", "POST", "CrossEncoder Reranker"),
        ]
        
        for path, method, name in endpoints:
            try:
                if method == "GET":
                    r = requests.get(f"{FASTAPI_URL}{path}", timeout=2)
                    ok = r.status_code == 200
                else:
                    ok = alive  # POST endpoints only show online if server is running
                color = "#10b981" if ok else "#ef4444"
                dot = "●" if ok else "●"
                st.markdown(f"""
                <div class="glass-card" style="padding:14px 20px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <span style="color:#94a3b8;font-size:0.78rem;">{method}</span>
                        <span style="color:#e2e8f0;font-weight:600;margin-left:10px;font-size:0.88rem;">{path}</span><br>
                        <span style="color:#475569;font-size:0.78rem;">{name}</span>
                    </div>
                    <span style="color:{color};font-size:0.9rem;">{dot} {'OK' if ok else 'DOWN'}</span>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.markdown(f"""
                <div class="glass-card" style="padding:14px 20px;margin-bottom:8px;">
                    <span style="color:#ef4444;">● DOWN</span> &nbsp; {path}
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Architecture Stack")
        stack = [
            ("🔷", "Java Spring Boot", "API Gateway · Redis · MyBatis", "#4facfe"),
            ("↕", "HTTP REST Bridge", "AIEngineClient · RestTemplate", "#8b5cf6"),
            ("🐍", "FastAPI (Python)", "Port 8000 · Auto-reload", "#10b981"),
            ("🔗", "LangGraph", "StateGraph · 4-node Agent Chain", "#f59e0b"),
            ("📊", "Pandas + yfinance", "Vectorized Signal Backtesting", "#06b6d4"),
            ("🤗", "HuggingFace", "cross-encoder/ms-marco-MiniLM-L-6-v2", "#ec4899"),
        ]
        
        for icon, name, desc, color in stack:
            st.markdown(f"""
            <div class="glass-card" style="padding:14px 20px;margin-bottom:8px;border-left:3px solid {color};">
                <div style="font-weight:600;color:#e2e8f0;font-size:0.88rem;">{icon} {name}</div>
                <div style="color:#475569;font-size:0.78rem;margin-top:3px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### Quick Links")
        st.markdown("""
        <div style="font-size:0.84rem;color:#475569;line-height:2.4;">
            📜 <a href="http://127.0.0.1:8000/docs" target="_blank" style="color:#4facfe;">Swagger API Documentation → http://127.0.0.1:8000/docs</a><br>
            📜 <a href="http://127.0.0.1:8000/redoc" target="_blank" style="color:#4facfe;">ReDoc → http://127.0.0.1:8000/redoc</a>
        </div>
        """, unsafe_allow_html=True)
