# Column types import - Integer number, ForeignKey doosri table ka reference
from sqlalchemy import Column, Integer, ForeignKey
# relationship tables ke beech connection banata hai
from sqlalchemy.orm import relationship

# Base class jo table banayega
from db import Base


# Farm_Fruit_Batch ek join table hai - Farm, Fruit aur Batch ko aapas mein jodta hai
# Ye many-to-many relationship handle karta hai
class Farm_Fruit_Batch(Base):
    __tablename__ = "Farm_Fruit_Batch"  # Table ka naam

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for this link
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)  # Farm ka ID (foreign key)
    fruit_id = Column(Integer, ForeignKey("fruits.id"), nullable=False)  # Fruit ka ID (foreign key)
    batch_id = Column(Integer, ForeignKey("batch.id"), nullable=False)  # Batch ka ID (foreign key)

    farm = relationship("Farm", back_populates="farm_fruit_batch_rls")  # Is link ka farm
    fruit = relationship("Fruit", back_populates="farm_fruit_batch_rls")  # Is link ka fruit
    batch = relationship("Batch", back_populates="farm_fruit_batch_rls")  # Is link ka batch
