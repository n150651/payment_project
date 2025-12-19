import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

DB_NAME = os.getenv("DB_NAME")

# --- 1. SOURCE CONFIGURATION (Writes) ---
SRC_HOST = os.getenv("SOURCE_HOST")
SRC_USER = os.getenv("SOURCE_USER")
SRC_PASS = os.getenv("SOURCE_PASSWORD")
SRC_PORT = os.getenv("SOURCE_PORT")

# Changed driver to +aiomysql
SOURCE_DB_URL = f"mysql+aiomysql://{SRC_USER}:{SRC_PASS}@{SRC_HOST}:{SRC_PORT}/{DB_NAME}"

engine_source = create_async_engine(
    SOURCE_DB_URL,
    pool_size=15,           # Increased for higher real-time throughput
    max_overflow=25,        # Capacity for sudden traffic spikes
    pool_recycle=3600,      # Prevent MySQL "wait_timeout" disconnects
    pool_pre_ping=True      # Authenticate connection health before use
)
AsyncSessionSource = async_sessionmaker(engine_source, expire_on_commit=False, class_=AsyncSession)

# --- 2. REPLICA CONFIGURATION (Read-Only) ---
REP_HOST = os.getenv("REPLICA_HOST")
REP_USER = os.getenv("REPLICA_USER")
REP_PASS = os.getenv("REPLICA_PASSWORD")
REP_PORT = os.getenv("REPLICA_PORT")

REPLICA_DB_URL = f"mysql+aiomysql://{REP_USER}:{REP_PASS}@{REP_HOST}:{REP_PORT}/{DB_NAME}"

engine_replica = create_async_engine(
    REPLICA_DB_URL,
    pool_size=20,           # More connections for reads/analytics
    max_overflow=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
AsyncSessionReplica = async_sessionmaker(engine_replica, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

# --- ASYNC DEPENDENCIES ---
async def get_write_db():
    """Use this for POST, PUT, DELETE operations on the Source DB."""
    async with AsyncSessionSource() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_read_db():
    """Use this for GET operations on the Replica DB (Scalability)."""
    async with AsyncSessionReplica() as session:
        try:
            yield session
        finally:
            await session.close()