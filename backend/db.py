# SQLAlchemy se create_engine import karte hain - ye database connection banata hai
from sqlalchemy import create_engine
# sessionmaker se database sessions create hote hain, declarative_base se models banate hain
from sqlalchemy.orm import sessionmaker, declarative_base

# Database ka URL - MSSQL server se connect hone ka address
# DESKTOP-VJ2R43U\VR_SERVER is computer ka naam, Fruitalyzer is database ka naam
DATABASE_URL = (
    "mssql+pyodbc://DESKTOP-VJ2R43U\\VR_SERVER/Fruitalyzer"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# Engine banate hain - ye actually database se connect karta hai
# echo=True means saare SQL queries console par print honge (debugging ke liye)
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal ek factory hai jo naye database sessions banati hai
# autocommit=False means changes manually commit karne honge
# autoflush=False means query se pehle automatically flush nahi hoga
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class - isse inherit karke saare models (tables) banenge
Base = declarative_base()


# get_db function har API request ke liye ek naya database session provide karta hai
# yield ka matlab hai ye ek generator hai - FastAPI ise dependency injection mein use karta hai
def get_db():
    db = SessionLocal()  # Naya session create karo
    try:
        yield db  # Session ko API function ko do
    finally:
        db.close()  # API request khatam hote hi session band karo
