
import pandas as pd
import joblib
import matplotlib.pyplot as plt

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
    confusion_matrix,
    ConfusionMatrixDisplay
)

# =====================================
# 1. PROJECT PATH
# =====================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR / "dataset" / "marine_multi_agent_1000.csv"
)

MODEL_PATH = BASE_DIR / "marine_model.joblib"

CONFUSION_MATRIX_PATH = (
    BASE_DIR / "confusion_matrix.png"
)

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

# =====================================
# 4. CHECK DATASET COLUMNS
# =====================================

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
# 5. PREPARE DATA
# =====================================

df = df.dropna(subset=[TARGET]).copy()

X = df[FEATURES]
y = df[TARGET]

print("\nInput Features:", len(FEATURES))

print("\nPrediction Classes:")
print(y.value_counts())

# =====================================
# 6. CATEGORICAL AND NUMERICAL DATA
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
# 7. DATA PREPROCESSING
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
# 8. RANDOM FOREST CLASSIFIER
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
# 9. TRAIN AND TEST SPLIT
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
# 10. TRAIN MODEL
# =====================================

print("\nTraining Random Forest Model...")

model.fit(X_train, y_train)

print("Training Completed Successfully!")

# =====================================
# 11. MODEL EVALUATION
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

# =====================================
# 12. CONFUSION MATRIX
# =====================================

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=model.classes_
)

print(cm)

# =====================================
# 13. VISUAL CONFUSION MATRIX
# =====================================

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=model.classes_
)

fig, ax = plt.subplots(figsize=(9, 7))

disp.plot(
    ax=ax,
    cmap="Blues",
    values_format="d",
    colorbar=True
)

plt.title(
    "BlueWatch - Random Forest Confusion Matrix"
)

plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")

plt.xticks(rotation=30, ha="right")

plt.tight_layout()

plt.savefig(
    CONFUSION_MATRIX_PATH,
    dpi=300,
    bbox_inches="tight"
)

print(
    "\nConfusion Matrix Image Saved:",
    CONFUSION_MATRIX_PATH
)

plt.show()

plt.close(fig)

# =====================================
# 14. SAVE TRAINED MODEL
# =====================================

joblib.dump(model, MODEL_PATH)

print("\n========== MODEL SAVED ==========")

print("Model Name: Random Forest Classifier")
print("Target: Final_Prediction")
print("Saved File:", MODEL_PATH)

print("\nBlueWatch Model Training Completed!")
