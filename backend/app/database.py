
import os


from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

load_dotenv()

host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "3306")
user = os.getenv("DB_USER", "root")
password = quote_plus(os.getenv("DB_PASSWORD", ""))
database = os.getenv("DB_NAME", "CriminalDB")

DATABASE_URL = (
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def test_connection():
    with engine.connect() as connection:
        return connection.execute(text("SELECT DATABASE()")).scalar()
