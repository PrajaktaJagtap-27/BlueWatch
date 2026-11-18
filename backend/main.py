
import sqlite3
import hashlib
import secrets
import hmac

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

from prediction import predict_marine_ecosystem
from weather_service import get_marine_weather


# =====================================
# DATABASE CONFIGURATION
# =====================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bluewatch.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def create_database():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """)

        connection.commit()

    finally:
        connection.close()


create_database()


# =====================================
# PASSWORD SECURITY
# =====================================

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    ).hex()


# =====================================
# FASTAPI APPLICATION
# =====================================

app = FastAPI(
    title="BlueWatch API",
    description="Marine Weather and Ecosystem Intelligence System",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =====================================
# SIGNUP INPUT
# =====================================

class SignupInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# =====================================
# LOGIN INPUT
# =====================================

class LoginInput(BaseModel):
    email: EmailStr
    password: str


# =====================================
# MARINE PREDICTION INPUT
# =====================================

class MarineInput(BaseModel):

    Region: str
    Season: str
    Weather: str

    Water_Temperature_C: float
    Salinity_PSU: float
    pH: float
    Dissolved_Oxygen_mg_L: float

    Wave_Height_m: float
    Current_Speed_m_s: float
    Chlorophyll_mg_m3: float

    Plastic_Pollution_Index: float
    Oil_Spill_Index: float
    Algae_Index: float

    Marine_Species: str
    Estimated_Population: int = Field(ge=0)
    Biodiversity_Index: float


# =====================================
# HOME API
# =====================================

@app.get("/")
def home():

    return {
        "message": "Welcome to BlueWatch API",
        "status": "Running"
    }


# =====================================
# HEALTH CHECK API
# =====================================

@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "project": "BlueWatch",
        "model": "Random Forest",
        "target": "Final_Prediction"
    }


# =====================================
# SIGNUP API
# =====================================

@app.post("/api/signup")
def signup(data: SignupInput):

    name = data.full_name.strip()
    email = str(data.email).strip().lower()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Enter a valid name."
        )

    salt = secrets.token_hex(16)
    password_hash = hash_password(data.password, salt)

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO users
            (full_name, email, password_hash, salt)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password_hash, salt)
        )

        connection.commit()

        return {
            "success": True,
            "message": "Account created successfully. Please login."
        }

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=409,
            detail="This email is already registered."
        )

    finally:
        connection.close()


# =====================================
# LOGIN API
# =====================================

@app.post("/api/login")
def login(data: LoginInput):

    email = str(data.email).strip().lower()

    connection = get_db_connection()

    try:
        user = connection.execute(
            """
            SELECT id, full_name, email, password_hash, salt
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    finally:
        connection.close()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    user_id, full_name, user_email, stored_hash, salt = user

    entered_hash = hash_password(data.password, salt)

    if not hmac.compare_digest(entered_hash, stored_hash):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user_id,
            "full_name": full_name,
            "email": user_email
        }
    }


# =====================================
# ML ECOSYSTEM PREDICTION API
# =====================================

@app.post("/api/predict")
def predict(data: MarineInput):

    try:
        input_data = data.model_dump()

        result = predict_marine_ecosystem(input_data)

        return {
            "success": True,
            "project": "BlueWatch",
            "prediction": result["prediction"],
            "confidence": result["confidence"]
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(error)}"
        )


# =====================================
# LIVE MARINE WEATHER API
# =====================================

@app.get("/api/marine")
async def marine_weather(location: str = "Mumbai"):

    try:

        result = await get_marine_weather(location)

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=f"Marine weather service error: {str(error)}"
        )
