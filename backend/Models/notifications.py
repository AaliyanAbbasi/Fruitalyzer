# datetime module se current time lenge notifications ke liye
from datetime import datetime

# SQLAlchemy column types - Integer, String, Boolean (True/False), DateTime, ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

# Base class jo table banayega
from db import Base


# Notification class "notifications" table represent karta hai
class Notification(Base):
    __tablename__ = "notifications"  # Table ka naam

    id = Column(Integer, primary_key=True, index=True)  # Unique notification ID

    landlord_id = Column(Integer, ForeignKey("landlord.id"), nullable=False)  # Ye notification kis user ke liye hai

    title = Column(String(200), nullable=False)  # Notification ka title

    message = Column(String(500), nullable=False)  # Notification ka message

    type = Column(String(50), nullable=False)  # Notification ki type (e.g., "alert", "info")

    is_read = Column(Boolean, default=False)  # Kya user ne notification read kar liya? False = unread

    timestamp = Column(DateTime, default=datetime.utcnow)  # Notification kab bheja gaya
