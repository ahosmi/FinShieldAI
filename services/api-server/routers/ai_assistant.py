"""FinShield AI — AI Investigation Assistant Router"""

import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx

router = APIRouter()
logger = logging.getLogger("ai-assistant")

RAG_URL = os.getenv("RAG_SERVICE_URL", "http://rag-pipeline:8001")


class ChatRequest(BaseModel):
    question: str
    context: Optional[dict] = None


class ExplainRequest(BaseModel):
    transaction: dict
    risk_result: Optional[dict] = None


async def _call_rag(endpoint: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{RAG_URL}{endpoint}", json=payload)
        resp.raise_for_status()
        return resp.json()


@router.post("/chat")
async def chat(req: ChatRequest):
    """Free-form investigator questions answered by RAG + LLM."""
    try:
        result = await _call_rag("/chat", {"question": req.question, "context": req.context})
        return result
    except httpx.HTTPError as e:
        logger.error(f"RAG service error: {e}")
        raise HTTPException(503, "AI assistant temporarily unavailable")


@router.post("/explain")
async def explain(req: ExplainRequest):
    """Generate fraud explanation for a specific transaction."""
    try:
        result = await _call_rag("/explain", {
            "transaction": req.transaction,
            "risk_result": req.risk_result or {},
        })
        return result
    except httpx.HTTPError as e:
        logger.error(f"RAG explain error: {e}")
        raise HTTPException(503, "AI explanation service temporarily unavailable")


@router.get("/health")
async def ai_health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{RAG_URL}/health")
            return resp.json()
    except Exception:
        return {"status": "unavailable"}
