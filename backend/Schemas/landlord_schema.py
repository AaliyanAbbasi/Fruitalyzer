# Pydantic se BaseModel import karte hain - ye data validation aur schema banane ke liye hai
from pydantic import BaseModel


# SignupRequest - jab naya user register karega to ye data chahiye
class SignupRequest(BaseModel):
    name: str       # User ka naam (string, zaroori)
    email: str      # User ki email (string, zaroori)
    password: str   # User ka password (string, zaroori)


# LoginRequest - jab user login karega to ye data chahiye
class LoginRequest(BaseModel):
    email: str      # User ki email
    password: str   # User ka password


# UpdateProfileRequest - jab user profile update karega to ye data de sakta hai
# Sab optional hain (None ho sakta hai) - jo field dena hai woh do
class UpdateProfileRequest(BaseModel):
    name: str | None = None          # Naya naam (optional)
    city: str | None = None          # Naya city (optional)
    phone_number: str | None = None  # Naya phone number (optional)
    email: str | None = None         # Naya email (optional)
    password: str | None = None      # Naya password (optional)
