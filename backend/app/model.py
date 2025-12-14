import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from pathlib import Path

MODEL_PATH = Path("models/budget_model.pkl")

def train_and_save_model(csv_path="data/sample_data.csv"):
    """Train a Random Forest model from sample data and save it."""
    data = pd.read_csv(csv_path)
    X = data[['income', 'fixed_expenses', 'savings_goal', 'months_to_goal']]
    Y = data[['food_pct', 'entertainment_pct', 'shopping_pct']]

    model = RandomForestRegressor(random_state=42)
    model.fit(X, Y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("✅ Model Trained and Saved")

def load_model():
    """Load the trained model, or train it if not found."""
    if not MODEL_PATH.exists():
        print("⚠️ Model not found — training a new one.")
        train_and_save_model()
    return joblib.load(MODEL_PATH)