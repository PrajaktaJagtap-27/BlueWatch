
import joblib
import pandas as pd

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "marine_model.joblib"

FEATURES = [
    "Region",
    "Season",
    "Weather",
    "Water_Temperature_C",
    "Salinity_PSU",
    "pH",
    "Dissolved_Oxygen_mg_L",
    "Wave_Height_m",
    "Current_Speed_m_s",
    "Chlorophyll_mg_m3",
    "Plastic_Pollution_Index",
    "Oil_Spill_Index",
    "Algae_Index",
    "Marine_Species",
    "Estimated_Population",
    "Biodiversity_Index"
]


# Load trained model
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model not found. Run python train_model.py first."
    )

model = joblib.load(MODEL_PATH)


def predict_marine_ecosystem(input_data):

    # Convert input into DataFrame
    input_df = pd.DataFrame(
        [input_data],
        columns=FEATURES
    )

    # Generate prediction
    prediction = model.predict(input_df)[0]

    # Calculate class probabilities
    probabilities = model.predict_proba(input_df)[0]

    classes = model.named_steps["classifier"].classes_

    confidence = {
        str(label): round(float(prob) * 100, 2)
        for label, prob in zip(classes, probabilities)
    }

    return {
        "prediction": str(prediction),
        "confidence": confidence
    }
