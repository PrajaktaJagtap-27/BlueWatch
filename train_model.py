
import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# =====================================
# 1. PROJECT PATH
# =====================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR / "dataset" / "marine_multi_agent_1000.csv"
)

MODEL_PATH = BASE_DIR / "marine_model.joblib"

# =====================================
# 2. LOAD DATASET
# =====================================

print("\nLoading Marine Dataset...")

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

df.columns = df.columns.str.strip()

print("Dataset loaded successfully!")
print("Dataset Shape:", df.shape)

# =====================================
# 3. DEFINE INPUT FEATURES
# =====================================

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

TARGET = "Final_Prediction"

# Check dataset columns
required_columns = FEATURES + [TARGET]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns in dataset: {missing_columns}"
    )

# =====================================
# 4. PREPARE DATA
# =====================================

df = df.dropna(subset=[TARGET]).copy()

X = df[FEATURES]
y = df[TARGET]

print("\nInput Features:", len(FEATURES))

print("\nPrediction Classes:")
print(y.value_counts())

# =====================================
# 5. CATEGORICAL AND NUMERICAL DATA
# =====================================

categorical_features = [
    "Region",
    "Season",
    "Weather",
    "Marine_Species"
]

numerical_features = [
    col for col in FEATURES
    if col not in categorical_features
]

# =====================================
# 6. DATA PREPROCESSING
# =====================================

numerical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    )
])

categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="most_frequent")
    ),
    (
        "encoder",
        OneHotEncoder(handle_unknown="ignore")
    )
])

preprocessor = ColumnTransformer([
    (
        "categorical",
        categorical_pipeline,
        categorical_features
    ),
    (
        "numerical",
        numerical_pipeline,
        numerical_features
    )
])

# =====================================
# 7. RANDOM FOREST CLASSIFIER
# =====================================

classifier = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", classifier)
])

# =====================================
# 8. TRAIN AND TEST SPLIT
# =====================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining Records:", len(X_train))
print("Testing Records:", len(X_test))

# =====================================
# 9. TRAIN MODEL
# =====================================

print("\nTraining Random Forest Model...")

model.fit(X_train, y_train)

print("Training Completed Successfully!")

# =====================================
# 10. MODEL EVALUATION
# =====================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n========== MODEL RESULTS ==========")

print(f"Model Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)

print("\nConfusion Matrix:")

print(confusion_matrix(y_test, y_pred))

# =====================================
# 11. SAVE TRAINED MODEL
# =====================================

joblib.dump(model, MODEL_PATH)

print("\n========== MODEL SAVED ==========")

print("Model Name: Random Forest Classifier")
print("Target: Final_Prediction")
print("Saved File:", MODEL_PATH)

print("\nBlueWatch Model Training Completed!")
