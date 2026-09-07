# Fruitalyzer Project Explanation (Roman Urdu)

## Project Kya Hai?

Fruitalyzer ek **FastAPI** framework mein bana hua backend project hai jo **fruit quality detection** aur **category classification** karta hai. Ye machine learning ka use karke fruits ko grade A, B, C mein classify karta hai aur saath hi fruit ki category (jaise red_apple, green_apple, banana, chaunsa, sindhri, anwar ratol) bhi identify karta hai.

---

## Project Structure

```
fyp_backend/
│
├── router_main.py              # Main entry point - yahan se app start hoti hai
├── db.py                       # Database connection (MSSQL)
├── requirements.txt            # Required Python packages ki list
├── requirements_ml.txt         # ML ke liye extra packages
│
├── Controllers/                # Business logic - har feature ka logic yahan hai
│   ├── Lanlord_controller.py      # User signup/login/profile
│   ├── Farm_controller.py         # Farm management
│   ├── Batch_controller.py        # Batch (harvest session) management
│   ├── prediction_controller.py   # ML prediction logic
│   └── Notification_controller.py # Notifications
│
├── Models/                     # Database tables ki SQLAlchemy models
│   ├── Landlord.py             # User table
│   ├── Farm.py                 # Farm table
│   ├── Batch.py                # Batch table
│   ├── Fruit.py                # Fruit types table
│   ├── Farm_Fruit_Batch.py     # Many-to-many relationship table
│   ├── Prediction.py           # Prediction results table
│   └── notifications.py        # Notifications table
│
├── Schemas/                    # Pydantic models - request/response validation
│   ├── landlord_schema.py
│   ├── farm_schema.py
│   ├── batch_schema.py
│   ├── prediction_schema.py
│   └── notification_schema.py
│
├── FruitGrade_Dataset/         # ML pipeline - yahan model training aur inference hoti hai
│   └── ml/
│       ├── classification/
│       │   └── predictor.py    # Inference engine - image ko predict karta hai
│       ├── models/
│       │   └── model_builder.py # EfficientNet-B0 model ka code
│       ├── training/
│       │   ├── train_pipeline.py # Model training ka code
│       │   └── data_loader.py    # Dataset loading aur preprocessing
│       ├── utils/
│       │   └── helpers.py        # Utility functions
│       └── Scripts/
│           └── test_quality_model.py # Model test karne ka script
│
├── configs/
│   └── config.yaml             # ML model ke hyperparameters
│
└── uploads/predictions/        # Prediction images yahan save hoti hain
```

---

## Har File Ka Kaam

### 1. `router_main.py`
- **FastAPI app** create karta hai
- Saare **API endpoints** yahan define hain:
  - `/sign_up` - User register
  - `/login` - User login
  - `/Add_farm` - Naya farm add
  - `/predict` - Image upload karke prediction lena
  - `/predictions` - Saari predictions dekhna
  - `/start_batch_session` - Batch session start
  - `/stop_batch_session` - Batch session stop
  - Aur bhi 20+ endpoints hain
- Server **port 5000** par run hota hai

### 2. `db.py`
- **SQL Server** se connection establish karta hai
- SQLAlchemy ORM use hota hai
- Database URL: `mssql+pyodbc://DESKTOP-VJ2R43U\VR_SERVER/Fruitalyzer`

### 3. `Controllers/` - Business Logic

**Lanlord_controller.py:**
- `sign_up()` - Naya user create karta hai (name, email, password)
- `login()` - Email/password se user authenticate karta hai
- `update_profile()` - User profile update
- `get_landlord_by_id()` - User ki info fetch karta hai

**Farm_controller.py:**
- `add_farm()` - Naya farm add karta hai (landlord_id, name, province, city, type)
- `get_all_farms()` - Landlord ke saare farms fetch karta hai
- `get_farmby_id()` - Specific farm ki details
- `update_farm()` - Farm update
- `get_farm_by_location()` - Location ke according farms search

**Batch_controller.py:**
- `add_batch()` - Naya batch add (harvest session)
- `compare_batches()` - Batches ka comparison (total production ke hisaab se)
- `best_batch_of_year()` - Saal ka best batch
- `start_batch_session()` - Real-time conveyor belt session start
  - Jab koi fruit detect hota hai to counted hota hai
  - 3 stable frames ke baad count hota hai
  - 2 second cooldown hota hai
- `stop_batch_session()` - Session stop karta hai aur final counts save karta hai

**prediction_controller.py:**
- `predict()` - Sabse important function:
  1. Image ko upload folder mein save karta hai
  2. ML model ko predict karne deta hai
  3. Result database mein save karta hai
  4. Batch session status return karta hai
- `get_all_prediction()` - Saari predictions fetch
- `get_prediction_today()` - Aaj ki predictions
- `get_prediction_by_date()` - Kisi specific date ki predictions
- `update_prediction_grade()` - Prediction ka grade manually change kar sakte hain (A, B, C)

**Notification_controller.py:**
- `get_notifications()` - User ke notifications fetch karta hai

### 4. `Models/` - Database Structure

- **Landlord** - id, name, email, password
- **Farm** - id, Landlord_id, name, province, city, type
- **Batch** - id, total_weight, timestamp, class_A, class_B, class_C
- **Fruit** - id, name
- **Farm_Fruit_Batch** - Join table: farm_id, fruit_id, batch_id
- **Prediction** - id, fruit, grade, label, confidence, image_path, timestamp, batch_id, category
- **Notification** - id, landlord_id, title, message, type, is_read, timestamp

### 5. `FruitGrade_Dataset/ml/` - Machine Learning

**Model Architecture:**
- **EfficientNet-B0** backbone with **two output heads**:
  1. **Quality head** - 9 classes: apple_A, apple_B, apple_C, banana_A, banana_B, banana_C, mango_A, mango_B, mango_C
  2. **Category head** - 6 classes: red_apple, green_apple, banana, chaunsa, sindhri, anwar_ratol

**predictor.py (Inference):**
- Image ko 224x224 resize karta hai
- Normalize karta hai (mean, std)
- Model se quality aur category dono predict karta hai
- Confidence threshold < 40% → "unknown"
- Category confidence < 35% → "unknown"
- Fruit ke according allowed categories filter karta hai (e.g., apple sirf red_apple ya green_apple ho sakta hai)

**Training:**
- **Stage 1**: Sirf category head learn karta hai (backbone frozen)
- **Stage 2**: Backbone ke later layers fine-tune hote hain
- Data augmentation: random crop, flip, rotation, color jitter, blur
- Less data wali categories (green_apple, sindhri, anwar_ratol) ke liye virtual training targets

### 6. `configs/config.yaml`
- Saare ML hyperparameters yahan define hain
- Dataset paths, model name, training settings, inference settings

---

## Data Flow - End to End

```
User (Mobile App) 
    → POST /predict (image upload)
    → prediction_controller.predict()
        → Image save in uploads/predictions/
        → FruitQualityPredictor.predict(image)
            → Image preprocessing
            → EfficientNet-B0 model inference
            → Quality prediction + Category prediction
            → Result return
        → Database mein prediction save
    → JSON response (fruit, grade, category, confidence)
```

---

## Main Issues Jo The Aur Fix Kiye

1. **ModuleNotFoundError: No module named 'ml.classification'**
   - Cause: `.venv` mein ek aur `ml` package installed tha jo local `FruitGrade_Dataset/ml` ko shadow kar raha tha
   - Fix: `sys.path.insert(0, ...)` kiya instead of `sys.path.append(...)` taake local ml package ko priority mile

2. **Broken imports in prediction_controller.py**
   - `from sympy.integrals.meijerint_doc import category` - ye galat import tha, remove kiya

3. **Broken imports in Batch_controller.py**
   - `from logging import raiseExceptions` - remove kiya
   - `from pyexpat.errors import messages` - remove kiya

---

## Run Karne Ka Tarika

```powershell
# Virtual environment activate karo
.venv\Scripts\activate

# Server start karo
uvicorn router_main:app --reload --port 5000
```

Ya phir direct Python se:
```powershell
.venv\Scripts\python router_main.py
```
