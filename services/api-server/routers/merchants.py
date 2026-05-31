"""FinShield AI — Merchants Router"""

from fastapi import APIRouter, Depends, Query
from services.postgres_service import PostgresService, get_postgres

router = APIRouter()


@router.get("")
async def list_merchants(
    limit: int = Query(20, ge=1, le=100),
    pg: PostgresService = Depends(get_postgres),
):
    """Merchant risk table — sorted by fraud rate descending."""
    merchants = await pg.fetch_merchant_risk_summary(limit)
    return {"merchants": merchants}


@router.get("/{merchant_id}")
async def get_merchant(merchant_id: str, pg: PostgresService = Depends(get_postgres)):
    m = await pg.fetch_merchant(merchant_id)
    if not m:
        from fastapi import HTTPException
        raise HTTPException(404, f"Merchant {merchant_id} not found")
    return m
