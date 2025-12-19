from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import models
from database import engine_source, get_write_db, get_read_db
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

app = FastAPI(title="Payment API")
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
# Add this at the bottom of main.py
Instrumentator().instrument(app).expose(app)

# NOTE: In production, we don't usually use metadata.create_all with async 
# at runtime. We use migrations (Alembic). But for this step:
# models.Base.metadata.create_all(bind=engine_source) is handled outside or via sync engine.

app = FastAPI(title="Payment API (Async Source/Replica Architecture)")

# --- WRITE OPERATION (Goes to Source) ---
@app.post("/transactions/", response_model=models.TransactionResponse)
async def create_transaction(
    transaction: models.TransactionCreate, 
    db: AsyncSession = Depends(get_write_db),
    api_key: str = Depends(get_api_key) # <--- New Security Layer
):
    new_txn = models.TransactionDB(
        user_id=transaction.user_id,
        amount=transaction.amount,
        currency=transaction.currency,
        status="SUCCESS"
    )
    db.add(new_txn)
    
    # 'await' is the key: it pauses THIS request but keeps the SERVER active
    await db.commit() 
    await db.refresh(new_txn)
    return new_txn

# --- READ OPERATION (Goes to Replica) ---
@app.get("/transactions/{transaction_id}", response_model=models.TransactionResponse)
async def read_transaction(
    transaction_id: int, 
    db: AsyncSession = Depends(get_read_db) # <--- Uses Async Replica DB
):
    # In Async SQLAlchemy, we use 'select' instead of 'db.query'
    result = await db.execute(
        select(models.TransactionDB).filter(models.TransactionDB.id == transaction_id)
    )
    txn = result.scalars().first()
    
    if txn is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn

# --- HEALTH CHECK (Tests both DBs) ---
@app.get("/health")
async def health_check(
    write_db: AsyncSession = Depends(get_write_db),
    read_db: AsyncSession = Depends(get_read_db)
):
    health_status = {"status": "healthy", "checks": {}}
    
    # Check Source
    try:
        await write_db.execute(text("SELECT 1"))
        health_status["checks"]["source_db"] = "up"
    except Exception as e:
        health_status["checks"]["source_db"] = f"down: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Replica
    try:
        await read_db.execute(text("SELECT 1"))
        health_status["checks"]["replica_db"] = "up"
    except Exception as e:
        health_status["checks"]["replica_db"] = f"down: {str(e)}"
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
        
    return health_status