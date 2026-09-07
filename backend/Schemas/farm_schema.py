# Pydantic se BaseModel - data validation ke liye
from pydantic import BaseModel


# AddFarmRequest - naya farm add karne ke liye ye fields chahiyein
class AddFarmRequest(BaseModel):
    Landlord_id: int  # Farm kis landlord ka hai (ID)
    name: str          # Farm ka naam
    type: str          # Farm ki type (e.g., "mango", "apple")
    province: str      # Farm kis province mein hai
    city: str          # Farm kis city mein hai


# GetAllFarmsRequest - landlord ke saare farms lene ke liye
class GetAllFarmsRequest(BaseModel):
    landlord_id: int  # Jis landlord ke farms chahiye


# FarmLocationRequest - city ke according farms search karne ke liye
class FarmLocationRequest(BaseModel):
    city: str  # City ka naam


# UpdateFarmRequest - farm ki info update karne ke liye
# Sab fields optional hain - jo update karna hai woh do
class UpdateFarmRequest(BaseModel):
    name: str | None = None      # Naya farm naam (optional)
    type: str | None = None      # Naya type (optional)
    province: str | None = None  # Nayi province (optional)
    city: str | None = None      # Naya city (optional)
