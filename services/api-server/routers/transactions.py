"""FinShield AI — Transactions Router"""

from fastapi import APIRouter, Depends, Query
from services.postgres_service import PostgresService, get_postgres

router = APIRouter()


@router.get("")
async def list_transactions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    pg: PostgresService = Depends(get_postgres),
):
    txns = await pg.fetch_transactions(limit, offset)
    return {"transactions": txns, "count": len(txns)}


@router.get("/risk-distribution")
async def risk_distribution(pg: PostgresService = Depends(get_postgres)):
    """Counts by risk tier for donut chart."""
    dist = await pg.fetch_risk_distribution()
    return dist


@router.get("/fraud-by-type")
async def fraud_by_type(pg: PostgresService = Depends(get_postgres)):
    """Fraud count grouped by fraud_scenario for bar chart."""
    data = await pg.fetch_fraud_by_type()
    return data


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str, pg: PostgresService = Depends(get_postgres)):
    txn = await pg.fetch_transaction(transaction_id)
    if not txn:
        from fastapi import HTTPException
        raise HTTPException(404, f"Transaction {transaction_id} not found")
    return txn
