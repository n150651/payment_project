from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine_source, get_write_db, get_read_db
from sqlalchemy import text

# Create tables ONLY on the Source (Replica will copy them automatically)
models.Base.metadata.create_all(bind=engine_source)

app = FastAPI(title="Payment API (Source/Replica Architecture)")

# --- WRITE OPERATION (Goes to Source) ---
@app.post("/transactions/", response_model=models.TransactionResponse)
def create_transaction(
    transaction: models.TransactionCreate, 
    db: Session = Depends(get_write_db) # <--- Uses Source DB
):
    new_txn = models.TransactionDB(
        user_id=transaction.user_id,
        amount=transaction.amount,
        currency=transaction.currency,
        status="SUCCESS"
    )
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)
    return new_txn

# --- READ OPERATION (Goes to Replica) ---
@app.get("/transactions/{transaction_id}", response_model=models.TransactionResponse)
def read_transaction(
    transaction_id: int, 
    db: Session = Depends(get_read_db) # <--- Uses Replica DB
):
    txn = db.query(models.TransactionDB).filter(models.TransactionDB.id == transaction_id).first()
    if txn is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn

@app.get("/health")
def health_check(
    write_db: Session = Depends(get_write_db),
    read_db: Session = Depends(get_read_db)
):
    health_status = {"status": "healthy", "checks": {}}
    
    try:
        # Test Source (Write)
        write_db.execute(text("SELECT 1"))
        health_status["checks"]["source_db"] = "up"
    except Exception as e:
        health_status["checks"]["source_db"] = f"down: {str(e)}"
        health_status["status"] = "unhealthy"

    try:
        # Test Replica (Read)
        read_db.execute(text("SELECT 1"))
        health_status["checks"]["replica_db"] = "up"
    except Exception as e:
        health_status["checks"]["replica_db"] = f"down: {str(e)}"
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
        
    return health_status