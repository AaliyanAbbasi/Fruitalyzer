# SQLAlchemy se column types import karte hain - Integer number ke liye, String text ke liye
from sqlalchemy import Column, Integer, String
# relationship do tables ko aapas mein jodne ke liye (foreign key relations)
from sqlalchemy.orm import relationship

# Base ko import karte hain jisse ye model database table banega
from db import Base


# Landlord class ek SQLAlchemy model hai - "landlord" table represent karta hai
class Landlord(Base):
    __tablename__ = "landlord"  # Table ka naam database mein

    id = Column(Integer, primary_key=True, index=True)  # Unique ID, primary key, query fast karne ke liye index
    name = Column(String(100), nullable=False)  # User ka naam, 100 chars, null nahi ho sakta
    email = Column(String(100), unique=True, index=True)  # Email, unique (duplicate nahi), indexed
    password = Column(String(100), nullable=False)  # Password, 100 chars, zaroori hai

    farm_rls = relationship("Farm", back_populates="landlord_rls")  # Is landlord ke saare farms ki list
