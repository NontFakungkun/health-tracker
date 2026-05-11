import pandas as pd
from pathlib import Path
from datetime import date

DATA_DIR = Path(__file__).parent.parent / "data"

NUTRITION_LOG = DATA_DIR / "nutrition_log.csv"
WORKOUT_LOG   = DATA_DIR / "workout_log.csv"
WEIGHT_LOG    = DATA_DIR / "weight_log.csv"
FOOD_DB       = DATA_DIR / "food_database.csv"

NUTRITION_COLS = ["date", "meal", "food_name", "calories", "protein_g", "carbs_g", "fat_g", "quantity", "unit", "notes"]
WORKOUT_COLS   = ["date", "workout_name", "exercise_name", "set_number", "reps", "weight_kg", "notes"]
WEIGHT_COLS    = ["date", "weight_kg", "body_fat_pct", "notes"]


# ── Supabase client (created once, reused) ─────────────────────────────────

def _get_supabase():
    try:
        import streamlit as st
        from supabase import create_client
        url = st.secrets.get("supabase_url", "")
        key = st.secrets.get("supabase_key", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def _to_records(df: pd.DataFrame, cols: list) -> list:
    """Convert DataFrame rows to clean dicts safe for Supabase insert."""
    out = []
    available = [c for c in cols if c in df.columns]
    for _, row in df[available].iterrows():
        rec = {}
        for k, v in row.items():
            if isinstance(v, date):
                rec[k] = str(v)
            elif isinstance(v, float) and pd.isna(v):
                rec[k] = None
            elif v is None:
                rec[k] = None
            else:
                rec[k] = v
        out.append(rec)
    return out


def _pull_from_supabase(table: str, cols: list) -> pd.DataFrame | None:
    """Fetch all rows from Supabase table. Returns None if unavailable."""
    sb = _get_supabase()
    if sb is None:
        return None
    try:
        resp = sb.table(table).select("*").execute()
        if not resp.data:
            return pd.DataFrame(columns=cols)
        df = pd.DataFrame(resp.data).drop(columns=["id"], errors="ignore")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.date
        for c in cols:
            if c not in df.columns:
                df[c] = None
        return df[cols]
    except Exception:
        return None


def _push_to_supabase(table: str, df: pd.DataFrame, cols: list):
    """Full replace: delete all rows then re-insert current dataframe."""
    sb = _get_supabase()
    if sb is None:
        return
    try:
        sb.table(table).delete().gte("id", 0).execute()
        if not df.empty:
            records = _to_records(df, cols)
            for i in range(0, len(records), 100):
                sb.table(table).insert(records[i:i + 100]).execute()
    except Exception:
        pass  # never crash the app if Supabase is down


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ── Nutrition log ───────────────────────────────────────────────────────────

def load_nutrition_log() -> pd.DataFrame:
    _ensure_data_dir()
    sb_df = _pull_from_supabase("nutrition_log", NUTRITION_COLS)

    if sb_df is not None:
        # Auto-migrate: if Supabase is empty but local CSV has data, upload it
        if sb_df.empty and NUTRITION_LOG.exists():
            local = pd.read_csv(NUTRITION_LOG)
            if not local.empty:
                _push_to_supabase("nutrition_log", local, NUTRITION_COLS)
                local["date"] = pd.to_datetime(local["date"]).dt.date
                return local
        return sb_df

    # Offline fallback
    if NUTRITION_LOG.exists():
        df = pd.read_csv(NUTRITION_LOG)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    return pd.DataFrame(columns=NUTRITION_COLS)


def save_nutrition_log(df: pd.DataFrame):
    _ensure_data_dir()
    df.to_csv(NUTRITION_LOG, index=False)
    _push_to_supabase("nutrition_log", df, NUTRITION_COLS)


# ── Workout log ─────────────────────────────────────────────────────────────

def load_workout_log() -> pd.DataFrame:
    _ensure_data_dir()
    sb_df = _pull_from_supabase("workout_log", WORKOUT_COLS)

    if sb_df is not None:
        if sb_df.empty and WORKOUT_LOG.exists():
            local = pd.read_csv(WORKOUT_LOG)
            if not local.empty:
                _push_to_supabase("workout_log", local, WORKOUT_COLS)
                local["date"] = pd.to_datetime(local["date"]).dt.date
                return local
        if not sb_df.empty:
            sb_df["weight_kg"] = pd.to_numeric(sb_df["weight_kg"], errors="coerce").fillna(0.0)
            sb_df["reps"]      = pd.to_numeric(sb_df["reps"],      errors="coerce").fillna(0)
        return sb_df

    if WORKOUT_LOG.exists():
        df = pd.read_csv(WORKOUT_LOG)
        df["date"]      = pd.to_datetime(df["date"]).dt.date
        df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(0.0)
        df["reps"]      = pd.to_numeric(df["reps"],      errors="coerce").fillna(0)
        return df
    return pd.DataFrame(columns=WORKOUT_COLS)


def save_workout_log(df: pd.DataFrame):
    _ensure_data_dir()
    df.to_csv(WORKOUT_LOG, index=False)
    _push_to_supabase("workout_log", df, WORKOUT_COLS)


# ── Weight log ──────────────────────────────────────────────────────────────

def load_weight_log() -> pd.DataFrame:
    _ensure_data_dir()
    sb_df = _pull_from_supabase("weight_log", WEIGHT_COLS)

    if sb_df is not None:
        if sb_df.empty and WEIGHT_LOG.exists():
            local = pd.read_csv(WEIGHT_LOG)
            if not local.empty:
                _push_to_supabase("weight_log", local, WEIGHT_COLS)
                local["date"] = pd.to_datetime(local["date"]).dt.date
                return local
        return sb_df

    if WEIGHT_LOG.exists():
        df = pd.read_csv(WEIGHT_LOG)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    return pd.DataFrame(columns=WEIGHT_COLS)


def save_weight_log(df: pd.DataFrame):
    _ensure_data_dir()
    df.to_csv(WEIGHT_LOG, index=False)
    _push_to_supabase("weight_log", df, WEIGHT_COLS)


# ── Food database ────────────────────────────────────────────────────────────

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
    _ensure_data_dir()
    df = load_food_db()
    factor = 100.0 / serving_g if serving_g > 0 else 1.0
    new_row = {
        "food_name":         food_name,
        "category":          category,
        "calories_per_100g": round(calories * factor, 1),
        "protein_per_100g":  round(protein  * factor, 2),
        "carbs_per_100g":    round(carbs    * factor, 2),
        "fat_per_100g":      round(fat      * factor, 2),
        "serving_size_g":    serving_g,
        "serving_name":      serving_name,
    }
    df = df[df["food_name"] != food_name]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FOOD_DB, index=False)


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_today_nutrition(df: pd.DataFrame = None) -> dict:
    if df is None:
        df = load_nutrition_log()
    today = date.today()
    today_df = df[df["date"] == today]
    return {
        "calories":  float(today_df["calories"].sum()),
        "protein_g": float(today_df["protein_g"].sum()),
        "carbs_g":   float(today_df["carbs_g"].sum()),
        "fat_g":     float(today_df["fat_g"].sum()),
        "entries":   int(len(today_df)),
    }


def get_last_workout_data(exercise_name: str, workout_name: str) -> pd.DataFrame:
    df = load_workout_log()
    mask = (df["exercise_name"] == exercise_name) & (df["workout_name"] == workout_name)
    exercise_df = df[mask]
    if exercise_df.empty:
        return pd.DataFrame()
    last_date = exercise_df["date"].max()
    return exercise_df[exercise_df["date"] == last_date].sort_values("set_number")
