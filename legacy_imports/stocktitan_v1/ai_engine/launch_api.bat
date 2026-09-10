@echo off
cd /d "c:\Users\Benjamindaoson\Music\us-stock-monitor-master\us-stock-monitor\ai_engine"
set HF_HOME=F:\us-stock-monitor\hf_cache
set TRANSFORMERS_CACHE=F:\us-stock-monitor\hf_cache
"F:\us-stock-monitor\ai_env\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
