# JSON module - data ko JSON format mein convert karne ke liye
import json
# datetime module - current time aur date ke liye
from datetime import datetime,timedelta,time

# FastAPI se HTTPException - errors return karne ke liye
from fastapi import HTTPException
# SQLAlchemy functions - desc (descending order), extract (date part nikalne ke liye)
from sqlalchemy import desc, extract

# Models import - database tables ke saath kaam karne ke liye
from Models.Batch import Batch
from Models.Farm import Farm
from Models.Fruit import Fruit
from Models.Farm_Fruit_Batch import Farm_Fruit_Batch
from Models.Prediction import Prediction


# BatchController mein saare batch-related functions hain
class BatchController:
    # active_batch_session ek class-level variable hai
    # Ye real-time conveyor belt session ka state store karta hai
    active_batch_session = {
        "started": False,      # Session start hua ya nahi
        "batch_id": None,       # Current batch ka ID
        "farm_id": None,        # Current farm ka ID
        "fruit_id": None,       # Current fruit ka ID
        "counts": {},           # Har grade ka count (e.g., {"apple_A": 5, "mango_B": 3})
        "last_prediction": None, # Last prediction ka label
        "stable_frames": 0,     # Kitni frames se same prediction aa raha hai
        "last_saved_time": 0    # Last count kab save hua (cooldown ke liye)
    }

    @staticmethod
    def add_batch(data, database):
        try:
            # Naya batch create karo
            new_batch = Batch(
                total_weight=data.total_weight,
                timestamp=datetime.utcnow(),  # Current time
                class_A=data.class_A,
                class_B=data.class_B,
                class_C=data.class_C
            )

            database.add(new_batch)    # Database mein add karo
            database.commit()          # Save karo
            database.refresh(new_batch)  # ID wapas lo

            # Farm-Fruit-Batch link banao (ye join table mein entry banayega)
            farm_fruit_batch_entry = Farm_Fruit_Batch(
                farm_id=data.farm_id,
                fruit_id=data.fruit_id,
                batch_id=new_batch.id
            )

            database.add(farm_fruit_batch_entry)
            database.commit()

            return {
                "message": "Batch added successfully",
                "batch_id": new_batch.id
            }

        except Exception as e:
            database.rollback()  # Koi error aya to sab wapas lo
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def compare_batches(database):
        # Total production calculate karo: class_A + class_B + class_C
        total_production = (
            Batch.class_A + Batch.class_B + Batch.class_C
        ).label("total_production")

        # Saare batches lo, total production descending order mein
        results = database.query(
            Batch.id,
            Batch.class_A,
            Batch.class_B,
            Batch.class_C,
            total_production  # Calculated field
        ).order_by(desc(total_production)).all()  # Sabse zyada production wala pehle

        return [
            {
                "batch_id": b.id,
                "class_A": b.class_A,
                "class_B": b.class_B,
                "class_C": b.class_C,
                "total_production": b.total_production  # Calculated value
            }
            for b in results
        ]

    @staticmethod
    def best_batch_of_year(data, database):
        year = data.year

        # Total production calculate karo
        total_production = (
            Batch.class_A + Batch.class_B + Batch.class_C
        )

        # Specific year ka best batch dhundho (sabse zyada production wala)
        batch = database.query(
            Batch.id,
            Batch.class_A,
            Batch.class_B,
            Batch.class_C,
            Batch.timestamp,
            total_production.label("total_production")
        ).filter(
            extract("year", Batch.timestamp) == year  # Sirf is year ke batches
        ).order_by(
            desc(total_production)  # Sabse zyada production wala pehle
        ).first()  # Sirf first (best) result lo

        if not batch:
            return {"message": "No batch found for this year"}

        return {
            "batch_id": batch.id,
            "class_A": batch.class_A,
            "class_B": batch.class_B,
            "class_C": batch.class_C,
            "total_production": batch.total_production,
            "date": batch.timestamp.strftime("%Y-%m-%d")
        }

    @staticmethod
    def create_batch_internal(farm_id, fruit_id, database):
        """Internal function - naya batch banata hai (API se direct call nahi hota)"""
        try:
            # Naya batch create karo with zero counts
            new_batch = Batch(
                total_weight="0",
                timestamp=datetime.utcnow(),
                class_A=0,
                class_B=0,
                class_C=0
            )

            database.add(new_batch)
            database.commit()
            database.refresh(new_batch)

            # Farm-Fruit-Batch link banao
            farm_fruit_batch_entry = Farm_Fruit_Batch(
                farm_id=farm_id,
                fruit_id=fruit_id,
                batch_id=new_batch.id
            )

            database.add(farm_fruit_batch_entry)
            database.commit()

            return {"success": True, "batch_id": new_batch.id}

        except Exception as exc:
            database.rollback()
            return {"success": False, "error": str(exc)}

    @staticmethod
    def get_all_batch(database):
        # Saare batches fetch karo
        batches = database.query(Batch).all()

        return [
            {
                "id": batch.id,
                "class_A": batch.class_A,
                "class_B": batch.class_B,
                "class_C": batch.class_C,
                "timestamp": batch.timestamp
            }
            for batch in batches
        ]

    @staticmethod
    def get_batches_report(data, database):
        selected_farm_id = data.farm_id

        # Multiple tables ko JOIN karke report banao
        query = database.query(
            Batch.id.label("batch_id"),
            Farm.name.label("farm_name"),
            Fruit.name.label("fruit_name"),
            Batch.class_A,
            Batch.class_B,
            Batch.class_C,
            Batch.timestamp
        ).join(
            Farm_Fruit_Batch, Farm_Fruit_Batch.batch_id == Batch.id  # Batch -> Farm_Fruit_Batch join
        ).join(
            Farm, Farm.id == Farm_Fruit_Batch.farm_id  # Farm_Fruit_Batch -> Farm join
        ).join(
            Fruit, Fruit.id == Farm_Fruit_Batch.fruit_id  # Farm_Fruit_Batch -> Fruit join
        )

        # Agar specific farm diya hai to sirf uske batches dikhao
        if selected_farm_id is not None:
            query = query.filter(Farm.id == selected_farm_id)

        batches = query.order_by(Batch.timestamp.desc()).all()

        return [
            {
                "batch_id": r.batch_id,
                "farm_name": r.farm_name,
                "fruit_name": r.fruit_name,
                "class_A": r.class_A,
                "class_B": r.class_B,
                "class_C": r.class_C,
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for r in batches
        ]

    @staticmethod
    def finalize_batch_internal(batch_id, counts, database):
        """Internal function - batch session khatam hone par final counts save karta hai"""
        try:
            # Batch dhundho
            batch = database.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                return {"error": "batch not found"}

            # Counts se classes calculate karo
            class_a_total = 0
            class_b_total = 0
            class_c_total = 0

            for key, value in counts.items():
                if "_" in key:
                    fruit_name, grade = key.split("_", 1)  # e.g., "apple_A" -> "apple" aur "A"

                    if grade == "A":
                        class_a_total += value
                    elif grade == "B":
                        class_b_total += value
                    elif grade == "C":
                        class_c_total += value

            batch.class_A = class_a_total
            batch.class_B = class_b_total
            batch.class_C = class_c_total

            total = class_a_total + class_b_total + class_c_total
            batch.total_weight = str(total)

            database.commit()

            return {
                "success": True,
                "batch_id": batch.id,
                "class_A": class_a_total,
                "class_B": class_b_total,
                "class_C": class_c_total,
                "total": total
            }

        except Exception as exc:
            database.rollback()
            return {"success": False, "error": str(exc)}

    @staticmethod
    def start_batch_session(data, database):
        """Real-time conveyor belt session start karta hai"""
        try:
            # Farm dhundho
            farm = database.query(Farm).filter(Farm.id == data.farm_id).first()
            if not farm:
                raise HTTPException(status_code=404, detail="farm not found")

            # Farm ki type (fruit) se fruit dhundho
            fruit = database.query(Fruit).filter(Fruit.name.ilike(farm.type)).first()
            if not fruit:
                raise HTTPException(status_code=404, detail="fruit not found in this farm")

            # Naya batch create karo
            batch_result = BatchController.create_batch_internal(
                farm_id=farm.id,
                fruit_id=fruit.id,
                database=database
            )
            if not batch_result.get("success"):
                raise HTTPException(status_code=500, detail=batch_result.get("error", "batch creation failed"))

            # Session state set karo
            BatchController.active_batch_session = {
                "started": True,
                "batch_id": batch_result["batch_id"],
                "farm_id": farm.id,
                "fruit_id": fruit.id,
                "counts": {},
                "last_prediction": None,
                "stable_frames": 0,
                "last_saved_time": 0
            }

            return {
                "message": "batch session started",
                "batch_id": batch_result["batch_id"],
                "farm_id": farm.id,
                "fruit_id": fruit.id,
                "fruit_name": fruit.name
            }

        except HTTPException:
            raise  # HTTPException ko waisa hi rehne do
        except Exception as e:
            database.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def weekly_report(data,database):
        try:
            week_start=datetime.strptime(data.week_start_date,"%y-%m-%d").date()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="week_start_date must be in yyy-mm-dd format"
            )
        week_end=week_start + timedelta(days=6)

        days_response=[]
        for offset in range(7):
            current_day=week_start+timedelta(days=offset)
            day_start=datetime.combine(current_day,time.min)
            day_end=datetime.combine(current_day,time.max)
            day_totals=BatchController._aggregate_variety_counts(
                landlord_id=data.landlord_id,
                farm_id=data.farm_id,
                database=database,
                date_from=day_start,
                date_to=day_end
            )
            days_response.append({
                "date":current_day.strftime("%y-%m-%x"),
                "varieties":BatchController._totals_toorderd_rows(day_totals)
            })
            week_start_datetime=datetime.combine(week_start,time.min)
            week_end_datetime=datetime.combine(week_end,time.max)
            week_totals=BatchController._aggregate_variety_counts(
                landlord_id=data.landlord_id,
                farm_id=data.farm_id,
                database=database,
                date_from=week_start_datetime,
                date_to=week_end_datetime
            )
            return{
                "week_start":week_start.strftime("%y-%m,%d"),
                "week_end":week_end.strftime("%y-%m,%d"),
                  "days":days_response,
                  "week_total":BatchController._total_to_ordered_rows(week_totals)
        }


    @staticmethod
    def stop_batch_session(database):
        """Batch session ko stop karta hai aur final counts save karta hai"""
        try:
            session = BatchController.active_batch_session

            if not session["started"]:
                raise HTTPException(status_code=400, detail="no active batch session")

            if session["batch_id"] is None:
                raise HTTPException(status_code=400, detail="no batch created for active session")

            # Session finalize karo (counts save karo)
            result = BatchController.finalize_batch_internal(
                batch_id=session["batch_id"],
                counts=session["counts"],
                database=database
            )

            if not result.get("success"):
                raise HTTPException(status_code=500, detail=result.get("error", "batch finalize failed"))

            # Percentages calculate karo
            total = result["total"]
            class_a_percentage = 0
            class_b_percentage = 0
            class_c_percentage = 0

            if total > 0:
                class_a_percentage = round((result["class_A"] / total) * 100)
                class_b_percentage = round((result["class_B"] / total) * 100)
                class_c_percentage = round((result["class_C"] / total) * 100)

            final_response = {
                "message": "batch finalized successfully",
                "batch_id": result["batch_id"],
                "class_A": result["class_A"],
                "class_B": result["class_B"],
                "class_C": result["class_C"],
                "total": total,
                "class_A_percentage": class_a_percentage,
                "class_B_percentage": class_b_percentage,
                "class_C_percentage": class_c_percentage,
                "counts": session["counts"]
            }

            # Session reset karo
            BatchController.active_batch_session = {
                "started": False,
                "batch_id": None,
                "farm_id": None,
                "fruit_id": None,
                "counts": {},
                "last_prediction": None,
                "stable_frames": 0,
                "last_saved_time": 0
            }

            return final_response

        except HTTPException:
            raise
        except Exception as e:
            database.rollback()
            raise HTTPException(status_code=500, detail=str(e))
