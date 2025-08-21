# scripts/database.py
import os
from sqlalchemy import create_engine

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'fpl_data.db')

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Create a SQLAlchemy engine
engine = create_engine(f'sqlite:///{DB_PATH}')

def get_db_engine():
    return engine