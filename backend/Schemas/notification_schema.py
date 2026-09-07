# Pydantic se BaseModel - data validation ke liye
from pydantic import BaseModel


# NotificationRequest - user ke notifications lene ke liye
class NotificationRequest(BaseModel):
    landlord_id: int  # Jis landlord ke notifications chahiye
