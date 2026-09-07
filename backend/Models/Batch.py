# Column types import karte hain - Integer number, String text, DateTime date/time ke liye
from sqlalchemy import Column, Integer, String, DateTime
# relationship do tables ke beech link banata hai
from sqlalchemy.orm import relationship

# Base class jo table banayega
from db import Base


# Batch class "batch" table represent karta hai - ye ek harvest session hai
class Batch(Base):
    __tablename__ = "batch"  # Table ka naam

    id = Column(Integer, primary_key=True, index=True)  # Unique batch ID
    total_weight = Column(String(100), nullable=False)  # Batch ka total weight (string mein)
    timestamp = Column(DateTime)  # Batch kab create hua
    class_A = Column(Integer, nullable=True)  # Kitne fruits Grade A hain
    class_B = Column(Integer, nullable=True)  # Kitne fruits Grade B hain
    class_C = Column(Integer, nullable=True)  # Kitne fruits Grade C hain

    farm_fruit_batch_rls = relationship("Farm_Fruit_Batch", back_populates="batch")  # Batch ke farm-fruit links
    predictions = relationship("Prediction", back_populates="batch")  # Is batch mein saari predictions
