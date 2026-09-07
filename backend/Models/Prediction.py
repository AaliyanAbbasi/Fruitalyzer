# datetime se current timestamp lenge
from datetime import datetime
# SQLAlchemy column types - Integer, Float (decimal number), ForeignKey, DateTime, String
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
# relationship tables ke beech link banata hai
from sqlalchemy.orm import relationship
# Base class jo table banayega
from db import Base


# Prediction class "predictions" table represent karta hai
# Ye table har ML prediction ka record store karta hai
class Prediction(Base):
    __tablename__ = "predictions"  # Table ka naam

    id = Column(Integer, primary_key=True, index=True)  # Unique prediction ID
    fruit = Column(String(100), nullable=True)  # Fruit ka naam (e.g., "apple", "mango")
    grade = Column(String(10), nullable=True)  # Grade: "A", "B", ya "C"
    label = Column(String(10), nullable=True)  # Full label: "apple_A", "mango_B" etc.
    confidence = Column(Float, nullable=False, default=0.0)  # Model kitna confident hai (0 to 1)
    status = Column(String(50), nullable=False, default="known")  # "known" ya "unknown"
    image_path = Column(String(500), nullable=False)  # Image ka file path jahan save hui hai
    timestamp = Column(DateTime, default=datetime.utcnow)  # Prediction kab hui
    batch_id = Column(Integer, ForeignKey("batch.id"), nullable=True)  # Kis batch ki prediction hai (optional)
    category = Column(String(50), nullable=True)  # Fruit category (e.g., "red_apple", "chaunsa")

    category_confidence = Column(
        Float,
        nullable=False,
        default=0.0,  # Category prediction kitni confident hai
    )

    batch = relationship("Batch", back_populates="predictions")  # Is prediction ka batch
