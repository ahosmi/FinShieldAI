import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import transactions, fraud_alerts, merchants, ai_assistant, websocket as ws_router
from services.kafka_consumer import FraudAlertConsumer
from services.redis_service import RedisService
from services.postgres_service import PostgresService
from routers.websocket import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("api-server")

redis_svc  = RedisService()
pg_svc     = PostgresService()
consumer   = FraudAlertConsumer(redis_svc, pg_svc, ws_manager)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_svc.connect()
    await pg_svc.connect()
    task = asyncio.create_task(consumer.start())
    logger.info("FinShield API Server — online")
    yield
    task.cancel()
    await redis_svc.disconnect()
    await pg_svc.disconnect()


app = FastAPI(
    title="FinShield AI API",
    description="Real-Time Fraud & Risk Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router,  prefix="/api/transactions", tags=["Transactions"])
app.include_router(fraud_alerts.router,  prefix="/api/alerts",       tags=["Fraud Alerts"])
app.include_router(merchants.router,     prefix="/api/merchants",    tags=["Merchants"])
app.include_router(ai_assistant.router,  prefix="/api/ai",           tags=["AI Assistant"])
app.include_router(ws_router.router,     tags=["WebSocket"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "finshield-api"}
