import logging
from typing import List
from models.schemas import HistoricalCaseDto, RerankRequest

logger = logging.getLogger(__name__)

# Initialize CrossEncoder - globally loaded once to save memory and latency
# Using a lightweight MS-MARCO model optimized for relevance ranking
try:
    from sentence_transformers import CrossEncoder
    logger.info("Initializing CrossEncoder Model (cross-encoder/ms-marco-MiniLM-L-6-v2)")
    # This might download ~90MB weights on first run
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
except Exception as e:
    logger.error(f"Failed to load sentence_transformers. Reranking will fallback. {e}")
    reranker = None

def rerank_candidates(request: RerankRequest) -> List[HistoricalCaseDto]:
    """
    Given a query and a set of preliminary candidates (from Java vector DB),
    re-scores all candidates using a genuine Cross-Encoder Transformer model.
    """
    logger.info(f"Reranking {len(request.candidates)} candidates for query: '{request.query}'")
    
    if not request.candidates:
        return []
        
    if reranker is None:
        logger.warning("Reranker model not loaded, returning top_k as-is.")
        return request.candidates[:request.top_k]

    # Prepare inputs: list of (query, candidate_document) tuples
    pairs = []
    for case in request.candidates:
        # Construct document context out of historical case
        document_text = f"Title: {case.title}. Analysis: {case.analysis}. Actual Impact: {case.actual_impact}"
        pairs.append((request.query, document_text))
        
    try:
        # Compute real Logit cross-encoder scores
        scores = reranker.predict(pairs)
        
        # Zp-pair candidates with their true relevance score
        scored_candidates = list(zip(scores, request.candidates))
        
        # Sort descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Debug logging the reordered documents
        for s, doc in scored_candidates[:request.top_k]:
            logger.debug(f"CrossEncoder Score {s:.4f} -> {doc.stock_code}: {doc.title}")
            
        # Return strictly the top_k
        return [case for score, case in scored_candidates[:request.top_k]]
        
    except Exception as e:
        logger.error(f"Reranking matrix computation failed: {e}")
        return request.candidates[:request.top_k]
