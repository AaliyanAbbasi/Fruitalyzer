# SQLAlchemy se column types import - Integer number, String text, ForeignKey doosri table ka reference
from sqlalchemy import Column, Integer, String, ForeignKey
# relationship do tables ke beech connection banata hai
from sqlalchemy.orm import relationship

# Base class jo table banayega database mein
from db import Base


# Farm class "farms" table represent karta hai
class Farm(Base):
    __tablename__ = "farms"  # Table ka naam

    id = Column(Integer, primary_key=True, index=True)  # Unique farm ID
    Landlord_id = Column(Integer, ForeignKey("landlord.id"))  # Ye farm kis landlord ka hai (foreign key)
    name = Column(String(100), nullable=False)  # Farm ka naam
    province = Column(String(100), nullable=False)  # Farm kis province mein hai
    city = Column(String(100), nullable=False)  # Farm kis city mein hai
    type = Column(String(100))  # Farm ki type (e.g., "mango", "apple" - jo fruit ugta hai)

    landlord_rls = relationship("Landlord", back_populates="farm_rls")  # Is farm ka landlord
    farm_fruit_batch_rls = relationship("Farm_Fruit_Batch", back_populates="farm")  # Is farm ke fruit-batch links
