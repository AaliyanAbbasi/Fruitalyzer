Fruitalyzer — Fruit Disease Detection & Quality Prediction System

Fruitalyzer is an AI-powered fruit detection, disease classification, and quality prediction system designed to automate fruit inspection and grading.

The system uses **Computer Vision, YOLO-based object detection, and CNN-based classification** to detect fruits, analyze their quality, and categorize them into different quality classes.

Key Features

*  Fruit Detection** using YOLO-based object detection
*  Fruit Quality Classification**
*  Disease Detection**
*  Automatic Fruit Counting**
*  Quality Grading**

  * Class A** — Export Quality
  * Class B** — Local Market Quality
  * Class C** — Diseased / Rejected
  * Batch Management**
  * Farm Management**
  * Production Records & Statistics**
  * Live Detection Support**
  * Web-based Dashboard**
  * Responsive Frontend**

##  System Architecture

```text
Camera / Image Input
        ↓
Image Preprocessing
        ↓
YOLO Object Detection
        ↓
Fruit Detection & Cropping
        ↓
CNN Classification
        ↓
Quality Classification
   ┌────┼────┐
   ↓    ↓    ↓
Class A Class B Class C
   ↓    ↓    ↓
Export  Local  Diseased/
Quality Market Rejected
        ↓
Data Aggregation
        ↓
Database
        ↓
Web Dashboard
```

## Technologies Used

### Frontend

* React.js
* Vite
* React Router
* Framer Motion
* Lucide React
* CSS / Responsive UI

### Backend

* Python
* Flask
* SQLAlchemy
* REST APIs

### Machine Learning & Computer Vision

* Python
* YOLO
* CNN
* NumPy
* Pandas
* OpenCV
* Machine Learning / Deep Learning

### Database

* Microsoft SQL Server

## Project Structure

```text
Fruitalyzer/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── Controllers/
│   ├── configs/
│   ├── ml/
│   ├── uploads/
│   ├── requirements.txt
│   ├── requirements_ml.txt
│   └── router_main.py
│
├── .gitignore
└── README.md
```

##  Supported Fruit Dataset

The project is designed to work with multiple fruit categories, including:

* Apple
* Watermelon
* Apricot
* Grapes
* Orange
* Tangerine
* Honeydew
* Fruiter
* Mango

The classification system assigns detected fruits to quality categories based on the trained model.

##  Quality Classification

| Class | Description          |
| ----- | -------------------- |
| **A** | Export Quality       |
| **B** | Local Market Quality |
| **C** | Diseased / Rejected  |

This grading system helps automate the inspection process and reduces the need for manual sorting.

##  Farm & Batch Management

Fruitalyzer also provides management functionality for agricultural production.

The system can maintain:

* Farm information
* Fruit production records
* Batch information
* Class-wise fruit counts
* Total production weight
* Timestamps
* Production summaries

This allows users to track fruit production and quality results from a centralized dashboard.

##  Production Monitoring

The system aggregates detection results and provides production statistics such as:

* Total detected fruits
* Class A count
* Class B count
* Class C count
* Batch information
* Production records

This information can be used to monitor fruit quality and production performance.

##  Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Fruitalyzer.git
cd Fruitalyzer
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

For machine-learning dependencies:

```bash
pip install -r requirements_ml.txt
```

Run the Flask backend:

```bash
python router_main.py
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will then be available through the Vite development server.

##  Environment Configuration

Before running the project, configure your database and application settings according to your local environment.

**Do not commit passwords, API keys, database credentials, or other sensitive information to GitHub.**

Use environment variables such as:

```text
DATABASE_URL=your_database_connection
SECRET_KEY=your_secret_key
```

##  Project Goal

The main goal of Fruitalyzer is to automate traditional fruit inspection and grading using Artificial Intelligence.

Instead of relying completely on manual inspection, the system provides an automated pipeline for:

**Detection → Classification → Quality Grading → Counting → Batch Recording → Production Monitoring**

This can help improve inspection efficiency, reduce manual effort, and provide more consistent quality assessment.

##  Future Improvements

Potential future improvements include:

* Real-time conveyor-belt integration
* Multiple-camera detection
* Improved disease classification
* Additional fruit categories
* Cloud deployment
* Mobile application integration
* Automated production reports
* Advanced analytics and visualization
* Improved model accuracy with larger datasets

##  Project

**Fruitalyzer — Disease Detection and Quality Prediction in Fruits**

Developed as an AI and Computer Vision based full-stack project combining:

**React + Flask + Machine Learning + Computer Vision + SQL Server**

---

⭐ If you find this project interesting, feel free to explore the repository.
