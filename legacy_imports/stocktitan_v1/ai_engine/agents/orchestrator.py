import logging
import yfinance as yf
from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from models.schemas import StockDataPayload, ComprehensiveReport

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """The state passed between agents in the graph."""
    stock_code: str
    raw_data: StockDataPayload
    market_context: str # Enriched via yfinance
    analyst_report: str
    risk_report: str
    final_decision: ComprehensiveReport

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm_structured = llm.with_structured_output(ComprehensiveReport)

def fetch_market_context_node(state: AgentState) -> AgentState:
    """New node: Enriches the Java payload with deep yfinance data."""
    symbol = state['stock_code']
    logger.info(f"Data Fetcher Agent gathering live context for: {symbol}")
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
        recent_close = hist['Close'].iloc[-1] if not hist.empty else "N/A"
        vol = hist['Volume'].iloc[-1] if not hist.empty else "N/A"
        
        context = f"""
        Company: {info.get('shortName', symbol)}
        Sector: {info.get('sector', 'Unknown')}
        Industry: {info.get('industry', 'Unknown')}
        Market Cap: {info.get('marketCap', 'Unknown')}
        Forward PE: {info.get('forwardPE', 'Unknown')}
        Recent Close Price: {recent_close}
        Recent Volume: {vol}
        52 Week High: {info.get('fiftyTwoWeekHigh', 'Unknown')}
        52 Week Low: {info.get('fiftyTwoWeekLow', 'Unknown')}
        """
    except Exception as e:
        logger.warning(f"yfinance enrichment failed for {symbol}: {e}")
        context = "Market context temporarily unavailable from yfinance."
        
    return {"market_context": context}

def analyst_node(state: AgentState) -> AgentState:
    logger.info(f"Analyst Agent running on: {state['stock_code']}")
    data = state["raw_data"]
    context = state.get("market_context", "")
    
    prompt = f"""
    Analyze {data.stock_code}.
    Current Gateway Price: {data.price}
    Recent Gateway News: {data.news}
    
    --- Deep Market Context ---
    {context}
    
    Provide an executive summary, investment thesis, and key catalysts.
    Be professional, data-driven, and objective.
    """
    response = llm.invoke([SystemMessage(content="You are a Senior Wall Street Analyst."), HumanMessage(content=prompt)])
    return {"analyst_report": response.content}

def risk_manager_node(state: AgentState) -> AgentState:
    logger.info(f"Risk Manager running on: {state['stock_code']}")
    data = state["raw_data"]
    context = state.get("market_context", "")
    
    prompt = f"""
    Assess risks for: {data.stock_code}.
    Current Gateway Price: {data.price}
    Recent Gateway News: {data.news}
    
    --- Deep Market Context ---
    {context}
    
    Identify all potential risk factors, macro and micro. Focus on volatility and fundamentals.
    """
    response = llm.invoke([SystemMessage(content="You are a strict Risk Manager."), HumanMessage(content=prompt)])
    return {"risk_report": response.content}

def advisor_node(state: AgentState) -> AgentState:
    logger.info(f"Advisor Agent running on: {state['stock_code']}")
    
    prompt = f"""
    Based on the analyst report and risk report, formulate a final comprehensive investment decision.
    
    --- Analyst Report ---
    {state.get("analyst_report")}
    
    --- Risk Report ---
    {state.get("risk_report")}
    
    Generate the structured ComprehensiveReport.
    """
    
    # We use structured output to strictly conform to our Pydantic model
    report = llm_structured.invoke([SystemMessage(content="You are the Lead Investment Advisor."), HumanMessage(content=prompt)])
    report.stock_code = state['stock_code']
    return {"final_decision": report}

# Define the Graph
def build_orchestrator() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("fetch_data", fetch_market_context_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("risk_manager", risk_manager_node)
    workflow.add_node("advisor", advisor_node)
    
    workflow.set_entry_point("fetch_data")
    workflow.add_edge("fetch_data", "analyst")
    workflow.add_edge("analyst", "risk_manager")
    workflow.add_edge("risk_manager", "advisor")
    workflow.add_edge("advisor", END)
    
    return workflow.compile()

graph = build_orchestrator()

def run_multi_agent_analysis(payload: StockDataPayload) -> ComprehensiveReport:
    """Executes the multi-agent graph with the given payload."""
    initial_state = {
        "stock_code": payload.stock_code,
        "raw_data": payload
    }
    
    # Run the graph
    app = build_orchestrator()
    final_state = app.invoke(initial_state)
    return final_state["final_decision"]
