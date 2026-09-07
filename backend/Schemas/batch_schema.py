# Pydantic se BaseModel - data validation ke liye
from pydantic import BaseModel


# AddBatchRequest - naya batch add karne ke liye
class AddBatchRequest(BaseModel):
    total_weight: str  # Batch ka total weight (string mein)
    class_A: int       # Grade A fruits ki quantity
    class_B: int       # Grade B fruits ki quantity
    class_C: int       # Grade C fruits ki quantity
    farm_id: int       # Kis farm ka batch hai
    fruit_id: int      # Kis fruit ka batch hai


# BestBatchRequest - saal ka best batch dhundhne ke liye
class BestBatchRequest(BaseModel):
    year: int  # Kis saal ka best batch chahiye


# BatchReportRequest - batch report lene ke liye
class BatchReportRequest(BaseModel):
    farm_id: int | None = None  # Kis farm ka report chahiye (optional - sab farms ka de sakta hai)


# StartBatchSessionRequest - real-time batch session start karne ke liye
class StartBatchSessionRequest(BaseModel):
    farm_id: int  # Kis farm par session start karna hai
