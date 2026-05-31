"""FinShield AI — RAG Pipeline FastAPI Service"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from rag_engine import FraudRAGEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag-pipeline")

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL  = os.getenv("LLM_MODEL", "mistral")

rag_engine: Optional[FraudRAGEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_engine
    logger.info(f"Initialising RAG engine (model={LLM_MODEL}, ollama={OLLAMA_URL})...")
    rag_engine = FraudRAGEngine(ollama_url=OLLAMA_URL, model=LLM_MODEL)
    logger.info("RAG engine ready.")
    yield


app = FastAPI(title="FinShield RAG Pipeline", version="1.0.0", lifespan=lifespan)


class ExplainRequest(BaseModel):
    transaction: dict
    risk_result: dict


class ChatRequest(BaseModel):
    question: str
    context: Optional[dict] = None


@app.post("/explain")
async def explain(req: ExplainRequest):
    if rag_engine is None:
        raise HTTPException(503, "RAG engine not ready")
    return rag_engine.explain_fraud(req.transaction, req.risk_result)


@app.post("/chat")
async def chat(req: ChatRequest):
    if rag_engine is None:
        raise HTTPException(503, "RAG engine not ready")
    return rag_engine.answer_question(req.question, req.context)


@app.get("/health")
async def health():
    return {"status": "ok", "model": LLM_MODEL}
