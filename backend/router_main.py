# FastAPI se Web Framework import - API banane ke liye
from fastapi import FastAPI, Body, Depends
# uvicorn - server chalane ke liye
import uvicorn
# UploadFile - file upload handle karne ke liye, HTTPException - errors ke liye
from fastapi import UploadFile, File, HTTPException
# SQLAlchemy Session - database interaction ke liye
from sqlalchemy.orm import Session
# Database connection aur Base class import
from db import Base, engine, get_db
# StaticFiles - uploaded images serve karne ke liye
from fastapi.staticfiles import StaticFiles

# Models import - saare database tables
from Models.Landlord import Landlord
from Models.Farm import Farm
from Models.Batch import Batch
from Models.Farm_Fruit_Batch import Farm_Fruit_Batch
from Models.Fruit import Fruit
from Models.notifications import Notification
from Models.Prediction import Prediction
# Saare tables create karo (agar pehle se nahi hain)
Base.metadata.create_all(bind=engine)

# Controllers import - business logic
from Controllers.Lanlord_controller import LandlordController
from Controllers.Farm_controller import FarmController
from Controllers.Batch_controller import BatchController
from Controllers.Notification_controller import NotificationController
from Controllers.prediction_controller import PredictionController

# Schemas import - request data validation
from Schemas.landlord_schema import LoginRequest, SignupRequest, UpdateProfileRequest
from Schemas.farm_schema import AddFarmRequest, GetAllFarmsRequest, FarmLocationRequest, UpdateFarmRequest
from Schemas.batch_schema import AddBatchRequest, BestBatchRequest, BatchReportRequest, StartBatchSessionRequest
from Schemas.notification_schema import NotificationRequest
from Schemas.prediction_schema import (
    PredictionIdRequest,
    PredictionBatchRequest,
    PredictionDateRequest,
    UpdatePredictionGradeRequest
)


# FastAPI app create karo
app = FastAPI(title="Fruitalyzer API")

# Uploads folder ko static serve karo (images direct URL se accessible hongi)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ── Root endpoint ──────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Fruitalyzer API Running"}


# ── Landlord (User) Routes ────────────────────────────────────────
@app.post("/sign_up")
def sign_up(data: SignupRequest, database: Session = Depends(get_db)):
    return LandlordController.sign_up(data, database)


@app.post("/login")
def login(data: LoginRequest, database: Session = Depends(get_db)):
    return LandlordController.login(data, database)


@app.put("/profile/{id}")
def update_profile(id: int, data: UpdateProfileRequest, database: Session = Depends(get_db)):
    return LandlordController.update_profile(id, data, database)


@app.get("/get_landlord_by_id/{l_id}")
def get_landlord_by_id(l_id: int, database: Session = Depends(get_db)):
    return LandlordController.get_landlord_by_id(l_id, database)


# ── Farm Routes ────────────────────────────────────────────────────
@app.post("/Add_farm")
def create_farm(data: AddFarmRequest, database: Session = Depends(get_db)):
    return FarmController.add_farm(data, database)


@app.post("/get_all_farms_of_landlord")
def get_all_farms(data: GetAllFarmsRequest, database: Session = Depends(get_db)):
    return FarmController.get_all_farms(data, database)


@app.get("/farm/{farm_id}")
def get_farmby_id(farm_id: int, database: Session = Depends(get_db)):
    return FarmController.get_farmby_id(farm_id, database)


@app.put("/update_farm/{farm_id}")
def update_farm(farm_id: int, data: UpdateFarmRequest, database: Session = Depends(get_db)):
    return FarmController.update_farm(farm_id, data, database)


@app.post("/farm_location")
def get_farm_by_location(data: FarmLocationRequest, database: Session = Depends(get_db)):
    return FarmController.get_farm_by_location(data, database)


# ── Batch Routes ───────────────────────────────────────────────────
@app.post("/add_batch")
def add_batch(data: AddBatchRequest, database: Session = Depends(get_db)):
    return BatchController.add_batch(data, database)


@app.get("/compare_batch")
def compare_batches(database: Session = Depends(get_db)):
    return BatchController.compare_batches(database)


@app.post("/best_batch")
def best_batch_of_year(data: BestBatchRequest, database: Session = Depends(get_db)):
    return BatchController.best_batch_of_year(data, database)


@app.get("/all_batch")
def get_all_batch(database: Session = Depends(get_db)):
    return BatchController.get_all_batch(database)


@app.post("/batch_report")
def get_batches_report(data: BatchReportRequest, database: Session = Depends(get_db)):
    return BatchController.get_batches_report(data, database)


@app.get("/batch")
def get_batch(database: Session = Depends(get_db)):
    return BatchController.get_all_batch(database)


@app.post("/start_batch_session")
def start_batch_session(data: StartBatchSessionRequest, database: Session = Depends(get_db)):
    """Real-time conveyor belt session start karo"""
    return BatchController.start_batch_session(data, database)


@app.post("/stop_batch_session")
def stop_batch_session(database: Session = Depends(get_db)):
    """Real-time conveyor belt session stop karo aur final counts save karo"""
    return BatchController.stop_batch_session(database)


# ── Notification Routes ────────────────────────────────────────────
@app.post("/get_notifications")
def get_notifications(data: NotificationRequest, database: Session = Depends(get_db)):
    return NotificationController.get_notifications(data, database)


# ── Prediction Routes ──────────────────────────────────────────────
@app.post("/predict")
async def predict(image: UploadFile = File(...), batch_id: int | None = None, database: Session = Depends(get_db)):
    """Image upload karo aur ML model se prediction lo"""
    print(image.content_type)  # Debug: image type console par print karo
    image_bytes = await image.read()  # Image bytes read karo
    return PredictionController.predict(image_byte=image_bytes, database=database, batch_id=batch_id)


@app.get("/predictions")
def get_all_predictions(database: Session = Depends(get_db)):
    return PredictionController.get_all_prediction(database)


@app.post("/prediction_by_id")
def get_prediction_by_id(data: PredictionIdRequest, database: Session = Depends(get_db)):
    return PredictionController.get_prediction_by_id(data.prediction_id, database)


@app.post("/prediction_by_batch")
def get_prediction_by_batch_id(data: PredictionBatchRequest, database: Session = Depends(get_db)):
    return PredictionController.get_prediction_by_batch_id(data.batch_id, database)


@app.get("/scans/today")
def get_scans_today(database: Session = Depends(get_db)):
    return PredictionController.get_prediction_today(database)


@app.post("/scans_by_date")
def get_scans_by_date(data: PredictionDateRequest, database: Session = Depends(get_db)):
    return PredictionController.get_prediction_by_date(data.selected_date, database)


@app.post("/update_prediction_grade")
def update_prediction_grade(data: UpdatePredictionGradeRequest, database: Session = Depends(get_db)):
    return PredictionController.update_prediction_grade(data, database)


# ── Temp Session Routes (Summary Page for Mobile App) ─────────────
# Ye routes temporary predictions handle karte hain jo kisi batch se attached nahi hain
# User jab bina batch start kiye predict karta hai to ye "temp" predictions hain
from pathlib import Path
from fastapi.responses import FileResponse
from pydantic import BaseModel as PydanticBaseModel


@app.post("/start_temp_session")
def start_temp_session():
    """Temporary session start karo (batch ke baghair)"""
    return {"message": "Temp session started", "session_id": 1}


@app.get("/debug_temp_count")
def debug_temp_count(database: Session = Depends(get_db)):
    """Debug endpoint: temp predictions ka count dikhata hai"""
    count = database.query(Prediction).filter(Prediction.batch_id == None).count()
    all_preds = database.query(Prediction).count()
    return {"temp_predictions_count": count, "total_predictions": all_preds}


@app.get("/get_temp_records")
def get_temp_records(since: str | None = None, session_id: int | None = None, database: Session = Depends(get_db)):
    """Temp predictions fetch karo (optional: since parameter se filter)"""
    from datetime import datetime as dt
    query = database.query(Prediction).filter(Prediction.batch_id == None)

    if since:
        try:
            since_dt = dt.fromisoformat(since.replace("Z", "+00:00")).replace(tzinfo=None)
            query = query.filter(Prediction.timestamp >= since_dt)
        except Exception:
            pass

    predictions = query.order_by(Prediction.timestamp.asc()).all()
    return [
        {
            "id": p.id,
            "image": Path(p.image_path).name,
            "grade": p.grade,
            "category": p.grade,
            "fruit_name": (p.category if p.category and p.category.lower() != "unknown" else p.fruit or "unknown").strip(),
            "confidence": f"{round(p.confidence * 100, 1)}%" if p.confidence <= 1.0 else f"{p.confidence}%",
            "fruit_category": p.category or "",
            "category_confidence": p.category_confidence or 0.0
        }
        for p in predictions
    ]


class UpdateTempRecordRequest(PydanticBaseModel):
    """Temp record ka grade update karne ke liye schema"""
    category: str


@app.put("/update_temp_record/{record_id}")
def update_temp_record(record_id: int, data: UpdateTempRecordRequest, database: Session = Depends(get_db)):
    """Temp prediction ka grade update karo"""
    p = database.query(Prediction).filter(Prediction.id == record_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Prediction record not found")
    if data.category not in ["A", "B", "C"]:
        raise HTTPException(status_code=400, detail="Grade must be A, B or C")
    p.grade = data.category
    if p.fruit is not None:
        p.label = f"{p.fruit}_{data.category}"
    database.commit()
    database.refresh(p)
    return {"message": "Grade updated successfully", "prediction_id": p.id, "fruit": p.fruit, "grade": p.grade}


@app.delete("/clear_temp")
def clear_temp(session_id: int | None = None, database: Session = Depends(get_db)):
    """Saari temp predictions delete karo"""
    database.query(Prediction).filter(Prediction.batch_id == None).delete()
    database.commit()
    return {"message": "Temp session cleared"}


class SaveTempToBatchRequest(PydanticBaseModel):
    """Temp predictions ko naye batch mein save karne ke liye schema"""
    farm_id: int
    session_id: int | None = None


@app.post("/save_temp_to_batch")
def save_temp_to_batch(data: SaveTempToBatchRequest, database: Session = Depends(get_db)):
    """
    Temp predictions ko ek naye batch mein convert karo.
    Jaise hi user "Save" button dabata hai, saari temp predictions ek batch ban jati hain.
    """
    try:
        from datetime import datetime as dt
        temp_predictions = database.query(Prediction).filter(Prediction.batch_id == None).all()
        if not temp_predictions:
            raise HTTPException(status_code=400, detail="No temporary predictions found to save")

        # Farm dhundho
        farm = database.query(Farm).filter(Farm.id == data.farm_id).first()
        if not farm:
            farm = database.query(Farm).first()
            if not farm:
                raise HTTPException(status_code=404, detail="No farm found in database. Please create a farm first.")

        # Grades count karo
        class_a = sum(1 for p in temp_predictions if p.grade == "A")
        class_b = sum(1 for p in temp_predictions if p.grade == "B")
        class_c = sum(1 for p in temp_predictions if p.grade == "C")
        total = class_a + class_b + class_c

        # Naya batch create karo
        new_batch = Batch(
            total_weight=str(total),
            timestamp=dt.utcnow(),
            class_A=class_a,
            class_B=class_b,
            class_C=class_c
        )
        database.add(new_batch)
        database.commit()
        database.refresh(new_batch)

        # Saari temp predictions ko is batch mein attach karo
        for p in temp_predictions:
            p.batch_id = new_batch.id

        # Unique fruit names ke liye links banao
        unique_fruit_names = set((p.fruit or "unknown").strip().lower() for p in temp_predictions)
        for fname in unique_fruit_names:
            capitalized_name = fname.capitalize()
            fruit_obj = database.query(Fruit).filter(Fruit.name.ilike(fname)).first()
            if not fruit_obj:
                fruit_obj = Fruit(name=capitalized_name)
                database.add(fruit_obj)
                database.commit()
                database.refresh(fruit_obj)
            link = Farm_Fruit_Batch(farm_id=farm.id, fruit_id=fruit_obj.id, batch_id=new_batch.id)
            database.add(link)

        database.commit()
        return {"message": "Batch saved successfully", "batch_id": new_batch.id}

    except HTTPException:
        raise
    except Exception as e:
        database.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ── Batch Images Routes ────────────────────────────────────────────
@app.get("/batch_images/{batch_id}")
def get_batch_images(batch_id: int, database: Session = Depends(get_db)):
    """Batch ki saari prediction images ki list do"""
    predictions = database.query(Prediction).filter(Prediction.batch_id == batch_id).all()
    return [
        {
            "id": p.id,
            "image": Path(p.image_path).name,
            "grade": p.grade,
            "category": p.category,
            "fruit_name": p.fruit or "unknown" or p.category,
            "confidence": p.confidence,
            "category_confidence": p.category_confidence,
        }
        for p in predictions
    ]


@app.get("/predict/images/{filename}")
def get_predict_image(filename: str):
    """Prediction image ko serve karo (URL se direct access)"""
    file_path = Path("uploads/predictions") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


# ── Server Start ───────────────────────────────────────────────────
if __name__ == "__main__":
    # Server ko port 5000 par start karo with auto-reload (code change par restart)
    uvicorn.run("router_main:app", host="0.0.0.0", port=5000, reload=True)
