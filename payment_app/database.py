import os
from dotenv import load_dotenv
from sqlalchemy  import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv()

# Common Config 
# HOST = os.getenv("DB_HOST")

DB_NAME = os.getenv("DB_NAME")

# --- 1. SOURCE CONFIGURATION ---
SRC_HOST = os.getenv("SOURCE_HOST") # <--- NEW
SRC_USER = os.getenv("SOURCE_USER")
SRC_PASS = os.getenv("SOURCE_PASSWORD")
SRC_PORT = os.getenv("SOURCE_PORT")

SOURCE_DB_URL = f"mysql+pymysql://{SRC_USER}:{SRC_PASS}@{SRC_HOST}:{SRC_PORT}/{DB_NAME}"

engine_source = create_engine(
    SOURCE_DB_URL,
    pool_size=5,
    max_overflow=10
)
SessionSource = sessionmaker(autocommit=False, autoflush=False, bind=engine_source)

# --- 2. REPLICA CONFIGURATION ---
REP_HOST = os.getenv("REPLICA_HOST") # <--- NEW
REP_USER = os.getenv("REPLICA_USER")
REP_PASS = os.getenv("REPLICA_PASSWORD")
REP_PORT = os.getenv("REPLICA_PORT")

REPLICA_DB_URL = f"mysql+pymysql://{REP_USER}:{REP_PASS}@{REP_HOST}:{REP_PORT}/{DB_NAME}"

engine_replica = create_engine(
    REPLICA_DB_URL,
    pool_size=10,
    max_overflow=20
)
SessionReplica = sessionmaker(autocommit=False, autoflush=False, bind=engine_replica)

Base = declarative_base()

# --- DEPENDENCIES ---
def get_write_db():
    db = SessionSource()
    try:
        yield db
    finally:
        db.close()

def get_read_db():
    db = SessionReplica()
    try:
        yield db
    finally:
        db.close()