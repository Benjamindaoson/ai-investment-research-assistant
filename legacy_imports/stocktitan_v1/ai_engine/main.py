import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models.schemas import StockDataPayload, ComprehensiveReport, SignalRecord, BacktestResult
from typing import List

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()

app = FastAPI(
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from agents.orchestrator import run_multi_agent_analysis
from services.backtesting import evaluate_signals_batch
from services.rag_service import rerank_candidates, RerankRequest, HistoricalCaseDto
from services.market_data import get_market_overview

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai_engine"}

@app.post("/api/v1/orchestrate", response_model=ComprehensiveReport)
def orchestrate_agents(payload: StockDataPayload):
    """
    Receives raw stock data from Java Gateway, 
    runs LangGraph Analyst->RiskManager->Advisor flow.
    """
    try:
        report = run_multi_agent_analysis(payload)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/backtest", response_model=BacktestResult)
def run_backtest(signals: List[SignalRecord]):
    """
    Receives batch of strategy signals from Java DB,
    computes vectorized hit rate and governance weights via Pandas.
    """
    try:
        result = evaluate_signals_batch(signals)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rerank", response_model=List[HistoricalCaseDto])
def run_reranking(request: RerankRequest):
    """
    Receives top 20 candidates from Java VectorStore, applies Cross-Encoder model,
    returns most accurate top 3 for LLM Context Prompting.
    """
    try:
        return rerank_candidates(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/overview")
def get_market_data():
    """
    Returns real-time indices and hot stocks for US, CN, and HK markets.
    """
    try:
        return get_market_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
