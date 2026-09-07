# Pydantic se BaseModel - data validation ke liye
from pydantic import BaseModel


# PredictionIdRequest - specific prediction ID se prediction lene ke liye
class PredictionIdRequest(BaseModel):
    prediction_id: int  # Prediction ka ID


# PredictionBatchRequest - batch ki saari predictions lene ke liye
class PredictionBatchRequest(BaseModel):
    batch_id: int  # Batch ka ID


# PredictionDateRequest - specific date ki predictions lene ke liye
class PredictionDateRequest(BaseModel):
    selected_date: str  # Date string (format: "YYYY-MM-DD")


# UpdatePredictionGradeRequest - prediction ka grade manually change karne ke liye
class UpdatePredictionGradeRequest(BaseModel):
    prediction_id: int  # Jis prediction ka grade change karna hai
    grade: str          # Naya grade: "A", "B", ya "C"
