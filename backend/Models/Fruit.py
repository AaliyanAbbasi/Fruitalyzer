# Column types import - Integer number, String text
from sqlalchemy import Column, Integer, String
# relationship tables ke beech link banata hai
from sqlalchemy.orm import relationship

# Base class jo table banayega
from db import Base


# Fruit class "fruits" table represent karta hai - ye fruit types ki list hai
class Fruit(Base):
    __tablename__ = "fruits"  # Table ka naam

    id = Column(Integer, primary_key=True, index=True)  # Unique fruit ID
    name = Column(String(100), nullable=False)  # Fruit ka naam (e.g., "Apple", "Mango", "Banana")

    farm_fruit_batch_rls = relationship("Farm_Fruit_Batch", back_populates="fruit")  # Is fruit ke farm-batch links
