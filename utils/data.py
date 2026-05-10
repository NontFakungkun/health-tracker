import pandas as pd
from pathlib import Path
from datetime import date

DATA_DIR = Path(__file__).parent.parent / "data"

NUTRITION_LOG = DATA_DIR / "nutrition_log.csv"
WORKOUT_LOG = DATA_DIR / "workout_log.csv"
WEIGHT_LOG = DATA_DIR / "weight_log.csv"
FOOD_DB = DATA_DIR / "food_database.csv"

NUTRITION_COLS = ["date", "meal", "food_name", "calories", "protein_g", "carbs_g", "fat_g", "quantity", "unit", "notes"]
WORKOUT_COLS = ["date", "workout_name", "exercise_name", "set_number", "reps", "weight_kg", "notes"]
WEIGHT_COLS = ["date", "weight_kg", "body_fat_pct", "notes"]


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_nutrition_log() -> pd.DataFrame:
    _ensure_data_dir()
    if NUTRITION_LOG.exists():
        df = pd.read_csv(NUTRITION_LOG)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    return pd.DataFrame(columns=NUTRITION_COLS)


def save_nutrition_log(df: pd.DataFrame):
    _ensure_data_dir()
    df.to_csv(NUTRITION_LOG, index=False)


def load_workout_log() -> pd.DataFrame:
    _ensure_data_dir()
    if WORKOUT_LOG.exists():
        df = pd.read_csv(WORKOUT_LOG)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(0.0)
        df["reps"] = pd.to_numeric(df["reps"], errors="coerce").fillna(0)
        return df
    return pd.DataFrame(columns=WORKOUT_COLS)


def save_workout_log(df: pd.DataFrame):
    _ensure_data_dir()
    df.to_csv(WORKOUT_LOG, index=False)


def load_weight_log() -> pd.DataFrame:
    _ensure_data_dir()
    if WEIGHT_LOG.exists():
        df = pd.read_csv(WEIGHT_LOG)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    return pd.DataFrame(columns=WEIGHT_COLS)


def save_weight_log(df: pd.DataFrame):
    _ensure_data_dir()
    df.to_csv(WEIGHT_LOG, index=False)


def load_food_db() -> pd.DataFrame:
    if FOOD_DB.exists():
        return pd.read_csv(FOOD_DB)
    return pd.DataFrame(columns=[
        "food_name", "category",
        "calories_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g",
        "serving_size_g", "serving_name",
    ])


def save_food_to_db(food_name: str, category: str, calories: float, protein: float,
                    carbs: float, fat: float, serving_g: float, serving_name: str):
    """Add or update a food entry in the persistent food database."""
    _ensure_data_dir()
    df = load_food_db()
    # Convert per-serving values to per-100g for consistent storage
    factor = 100.0 / serving_g if serving_g > 0 else 1.0
    new_row = {
        "food_name": food_name,
        "category": category,
        "calories_per_100g": round(calories * factor, 1),
        "protein_per_100g": round(protein * factor, 2),
        "carbs_per_100g": round(carbs * factor, 2),
        "fat_per_100g": round(fat * factor, 2),
        "serving_size_g": serving_g,
        "serving_name": serving_name,
    }
    # Replace if name already exists, otherwise append
    df = df[df["food_name"] != food_name]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FOOD_DB, index=False)


def get_today_nutrition(df: pd.DataFrame = None) -> dict:
    if df is None:
        df = load_nutrition_log()
    today = date.today()
    today_df = df[df["date"] == today]
    return {
        "calories": float(today_df["calories"].sum()),
        "protein_g": float(today_df["protein_g"].sum()),
        "carbs_g": float(today_df["carbs_g"].sum()),
        "fat_g": float(today_df["fat_g"].sum()),
        "entries": int(len(today_df)),
    }


def get_last_workout_data(exercise_name: str, workout_name: str) -> pd.DataFrame:
    df = load_workout_log()
    mask = (df["exercise_name"] == exercise_name) & (df["workout_name"] == workout_name)
    exercise_df = df[mask]
    if exercise_df.empty:
        return pd.DataFrame()
    last_date = exercise_df["date"].max()
    return exercise_df[exercise_df["date"] == last_date].sort_values("set_number")
