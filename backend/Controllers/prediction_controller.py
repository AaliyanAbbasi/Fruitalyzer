# sys module - Python path set karne ke liye
import sys
# datetime - timestamps ke liye
from datetime import datetime
# time - cooldown timer ke liye
import time
# io - bytes se image read karne ke liye
import io
# fastapi HTTPException - errors return karne ke liye
from fastapi import HTTPException
# PIL/Pillow - image processing ke liye
from PIL import Image
# uuid - unique filenames generate karne ke liye
from uuid import uuid4
# pathlib - file paths handle karne ke liye
from pathlib import Path

# BASE_DIR: is file se 2 levels up (Controllers/ -> fyp_backend/)
BASE_DIR = Path(__file__).resolve().parent.parent
# FruitGrade_Dataset ka path banao (jahan ml package hai)
FRUIT_DATASET_DIR = BASE_DIR / "FruitGrade_Dataset"
# Is path ko sys.path mein insert karo (starting mein taake priority ho)
# Taake "ml" package import ho sake (conflicting .venv ml package se bachne ke liye)
if str(FRUIT_DATASET_DIR) not in sys.path:
    sys.path.insert(0, str(FRUIT_DATASET_DIR))

# Models import - database tables ke saath kaam karne ke liye
from Models.Batch import Batch
from Models.Prediction import Prediction
# BatchController - session management ke liye
from Controllers.Batch_controller import BatchController
# ML predictor - actual fruit quality/category prediction ke liye
from ml.classification.predictor import FruitQualityPredictor


class PredictionController:
    # Global predictor - ek baar load hota hai, saare requests ke liye reuse hota hai
    predictor = FruitQualityPredictor()
    # Images yahan save hongi
    upload_dir = Path("uploads/predictions")

    @staticmethod
    def update_batch_session(result):
        """
        Batch session ko update karta hai.
        Ye real-time conveyor belt logic hai:
        - 3 stable frames (same prediction) ke baad count increment hota hai
        - 2 second ka cooldown hota hai duplicate count se bachne ke liye
        """
        session = BatchController.active_batch_session

        if not session["started"]:
            return None  # Session active nahi hai to kuch nahi karo

        if result.get("prediction") == "unknown":
            return None  # Unknown prediction ko count nahi karte

        fruit = result.get("fruit")
        grade = result.get("grade")
        if fruit is None or grade is None:
            return None

        current_prediction = f"{fruit}_{grade}"  # e.g., "apple_A"

        # Same prediction aa rahi hai to stable_frames increment karo
        if current_prediction == session["last_prediction"]:
            session["stable_frames"] += 1
        else:
            # Nayi prediction - reset karo
            session["last_prediction"] = current_prediction
            session["stable_frames"] = 1

        # 3 stable frames nahi hain to wait karo (noise filter)
        if session["stable_frames"] < 3:
            return {
                "counted": False,
                "reason": "waiting_for_stable_frames",
                "stable_frames": session["stable_frames"],
                "batch_id": session["batch_id"],
                "counts": session["counts"]
            }

        current_time = time.time()
        # 2 second cooldown (ek hi fruit baar baar count na ho)
        if current_time - session["last_saved_time"] < 2:
            return {
                "counted": False,
                "reason": "cooldown_active",
                "stable_frames": session["stable_frames"],
                "batch_id": session["batch_id"],
                "counts": session["counts"]
            }

        # Count increment karo
        if current_prediction not in session["counts"]:
            session["counts"][current_prediction] = 0
        session["counts"][current_prediction] += 1
        session["last_saved_time"] = current_time

        return {
            "counted": True,
            "counted_label": current_prediction,
            "stable_frames": session["stable_frames"],
            "batch_id": session["batch_id"],
            "counts": session["counts"]
        }

    @staticmethod
    def predict(image_byte, database, batch_id=None):
        """Main prediction function - image lo, model ko do, result save karo"""
        try:
            # Upload directory create karo agar exist nahi karti
            PredictionController.upload_dir.mkdir(parents=True, exist_ok=True)

            # Image ko bytes se open karo
            image = Image.open(io.BytesIO(image_byte)).convert("RGB")

            # Unique filename generate karo aur save karo
            filename = f"{uuid4().hex}.jpg"
            image_path = PredictionController.upload_dir / filename
            image.save(image_path)

            # ML model se prediction lo
            result = PredictionController.predictor.predict(image)

            # Batch session update karo (agar active ho to)
            batch_session_info = PredictionController.update_batch_session(result)
            if batch_session_info is not None:
                batch_id = batch_session_info["batch_id"]

            # Sirf tab save karo jab model ne kuch identify kiya ho
            prediction_label = result.get("prediction") or "unknown"
            should_save_prediction = prediction_label != "unknown"

            prediction_id = None

            if should_save_prediction:
                # Prediction record database mein save karo
                prediction_record = Prediction(
                    batch_id=batch_id,
                    image_path=str(image_path),
                    fruit=result.get("fruit"),
                    grade=result.get("grade"),
                    label=result.get("prediction"),
                    confidence=result.get("confidence", 0.0),
                    status="KNOWN" if result.get("prediction") != "unknown" else "UNKNOWN",
                    category=result.get("category"),
                    category_confidence=result.get("category_confidence", 0.0)
                )
                database.add(prediction_record)
                database.commit()
                database.refresh(prediction_record)
                prediction_id = prediction_record.id

            return {
                "message": "prediction successful",
                "prediction_id": prediction_id,
                "image_path": str(image_path),
                "result": result,
                "batch_session": batch_session_info
            }

        except Exception as e:
            database.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def get_all_prediction(database):
        """Saari predictions fetch karo, newest first"""
        predictions = database.query(Prediction).order_by(Prediction.timestamp.desc()).all()
        return [{
            "id": p.id,
            "batch_id": p.batch_id,
            "fruit": p.fruit,
            "category": p.category,
            "category_confidence": p.category_confidence,
            "grade": p.grade,
            "label": p.label,
            "confidence": p.confidence,
            "status": p.status,
            "image_path": p.image_path,
            "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for p in predictions]

    @staticmethod
    def format_group_scans(predictions, extra=None):
        """Predictions ko fruit ke hisaab se group karta hai"""
        group_dict = {}

        for p in predictions:
            fruit_name = p.fruit or "unknown"

            if fruit_name not in group_dict:
                group_dict[fruit_name] = []

            image_url = "/" + p.image_path.replace("\\", "/")

            group_dict[fruit_name].append({
                "id": p.id,
                "image_url": image_url,
                "grade": p.grade,
                "category": p.category,
                "label": p.label,
                "confidence": round(p.confidence, 4),
                "category_confidence": round(p.category_confidence or 0.0, 4),
                "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })

        groups = []
        for fruit_name, items in group_dict.items():
            groups.append({
                "fruit": fruit_name,
                "count": len(items),
                "items": items
            })

        response = {"groups": groups}
        if extra:
            response.update(extra)

        return response

    @staticmethod
    def get_prediction_by_id(prediction_id, database):
        """Specific prediction ID se prediction do"""
        p = database.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="prediction not found")

        return {
            "id": p.id,
            "batch_id": p.batch_id,
            "fruit": p.fruit,
            "grade": p.grade,
            "category": p.category,
            "label": p.label,
            "confidence": p.confidence,
            "status": p.status,
            "image_path": p.image_path,
            "category_confidence": p.category_confidence,
            "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def get_prediction_by_batch_id(batch_id, database):
        """Batch ID ke according saari predictions do"""
        predictions = (database.query(Prediction)
                       .filter(Prediction.batch_id == batch_id, Prediction.status == "KNOWN")
                       .order_by(Prediction.timestamp.desc()).all())

        return PredictionController.format_group_scans(predictions, {"batch_id": batch_id})

    @staticmethod
    def get_prediction_today(database):
        """Aaj ki saari predictions do"""
        today = datetime.utcnow().date()
        start_date = datetime.combine(today, datetime.min.time())  # Aaj start (midnight)
        end_date = datetime.combine(today, datetime.max.time())    # Aaj end (11:59 PM)

        predictions = database.query(Prediction).filter(
            Prediction.timestamp >= start_date,
            Prediction.timestamp <= end_date,
            Prediction.status == "KNOWN"
        ).order_by(Prediction.timestamp.desc()).all()

        return PredictionController.format_group_scans(predictions, {"date": today.strftime("%Y-%m-%d")})

    @staticmethod
    def get_prediction_by_date(selected_date, database):
        """Kisi specific date ki predictions do"""
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            start_date = datetime.combine(date_obj, datetime.min.time())
            end_date = datetime.combine(date_obj, datetime.max.time())

            predictions = database.query(Prediction).filter(
                Prediction.timestamp >= start_date,
                Prediction.timestamp <= end_date
            ).order_by(Prediction.timestamp.desc()).all()

            return PredictionController.format_group_scans(predictions, {"date": selected_date})

        except ValueError:
            raise HTTPException(status_code=400, detail="date format must be YYYY-MM-DD")

    @staticmethod
    def update_prediction_grade(data, database):
        """Prediction ka grade manually change karo (A, B, C)"""
        try:
            prediction = database.query(Prediction).filter(Prediction.id == data.prediction_id).first()
            if not prediction:
                raise HTTPException(status_code=404, detail="prediction not found")

            if data.grade not in ["A", "B", "C"]:
                raise HTTPException(status_code=400, detail="grade must be A, B or C")

            # Grade update karo
            prediction.grade = data.grade

            # Label bhi update karo (e.g., "apple_A")
            if prediction.fruit is not None:
                prediction.label = f"{prediction.fruit}_{data.grade}"

            # Batch ke total counts recalculate karo
            class_a = 0
            class_b = 0
            class_c = 0
            if prediction.batch_id is not None:
                batch_prediction = database.query(Prediction).filter(
                    Prediction.batch_id == prediction.batch_id,
                    Prediction.status == "KNOWN"
                ).all()

                for p in batch_prediction:
                    if p.grade == "A":
                        class_a += 1
                    elif p.grade == "B":
                        class_b += 1
                    elif p.grade == "C":
                        class_c += 1

                total = class_a + class_b + class_c

                # Batch table mein bhi counts update karo
                batch = database.query(Batch).filter(Batch.id == prediction.batch_id).first()
                if batch:
                    batch.class_A = class_a
                    batch.class_B = class_b
                    batch.class_C = class_c
                    batch.total_weight = str(total)

            database.commit()
            database.refresh(prediction)

            return {
                "message": "grade updated successfully",
                "prediction_id": prediction.id,
                "fruit": prediction.fruit,
                "grade": prediction.grade,
                "label": prediction.label,
                "batch_id": prediction.batch_id,
                "category": prediction.category,
                "class_A": class_a,
                "class_B": class_b,
                "class_C": class_c,
                "total": total
            }

        except HTTPException:
            raise
        except Exception as e:
            database.rollback()
            raise HTTPException(status_code=500, detail=str(e))


