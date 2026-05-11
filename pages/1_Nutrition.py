import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import date

from config import TARGETS
from utils.data import load_nutrition_log, save_nutrition_log, load_food_db, save_food_to_db
from utils.auth import require_login

st.set_page_config(page_title="Nutrition", page_icon="🥗", layout="wide")
require_login()
st.title("Nutrition Tracker")

today = date.today()
df_log = load_nutrition_log()
df_food = load_food_db()

# --- Summary bar at top ---
today_log = df_log[df_log["date"] == today]
t_cal = float(today_log["calories"].sum())
t_pro = float(today_log["protein_g"].sum())
t_carb = float(today_log["carbs_g"].sum())
t_fat = float(today_log["fat_g"].sum())

pro_target = TARGETS["protein_g"]
pro_min = TARGETS["protein_min_g"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Calories", f"{t_cal:.0f}", f"{TARGETS['calories'] - t_cal:.0f} remaining")
c2.metric("Protein", f"{t_pro:.0f}g", f"{pro_target - t_pro:.0f}g to goal ({pro_target}g)")
c3.metric("Carbs", f"{t_carb:.0f}g", f"{TARGETS['carbs_g'] - t_carb:.0f}g remaining")
c4.metric("Fat", f"{t_fat:.0f}g", f"{TARGETS['fat_g'] - t_fat:.0f}g remaining")

# Calorie bar
st.progress(min(t_cal / TARGETS["calories"], 1.0), text=f"Calories: {t_cal:.0f} / {TARGETS['calories']} kcal")

# Protein bar with range annotation
pro_pct = min(t_pro / pro_target, 1.0)
if t_pro >= pro_target:
    pro_status = "Goal reached!"
elif t_pro >= pro_min:
    pro_status = f"In range (min {pro_min}g met — push toward {pro_target}g)"
else:
    pro_status = f"Below minimum — need {pro_min - t_pro:.0f}g more to hit floor"
st.progress(pro_pct, text=f"Protein: {t_pro:.0f}g / {pro_target}g  —  {pro_status}")

st.divider()

# --- Add food ---
tab_db, tab_custom, tab_myfoods = st.tabs(["Add from Database", "Add New Meal", "Manage My Foods"])

with tab_db:
    if df_food.empty:
        st.warning("food_database.csv not found in /data folder.")
    else:
        col_search, col_cat = st.columns([3, 1])
        with col_search:
            search = st.text_input("Search food", placeholder="e.g. chicken, pad thai, egg...")
        with col_cat:
            all_cats = ["All"] + sorted(df_food["category"].dropna().unique().tolist())
            cat = st.selectbox("Category", all_cats)

        filtered = df_food.copy()
        if search:
            filtered = filtered[filtered["food_name"].str.contains(search, case=False, na=False)]
        if cat != "All":
            filtered = filtered[filtered["category"] == cat]

        if filtered.empty:
            st.info("No foods found. Try a different search or add a new meal in the 'Add New Meal' tab.")
        else:
            selected = st.selectbox("Select food", filtered["food_name"].tolist())
            row = filtered[filtered["food_name"] == selected].iloc[0]

            col_meal, col_qty, col_preview = st.columns([2, 2, 3])
            with col_meal:
                meal = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout", "Post-workout"], key="db_meal")
            with col_qty:
                default_g = float(row.get("serving_size_g", 100))
                serving_label = str(row.get("serving_name", "g"))
                qty = st.number_input(f"Quantity ({serving_label})", min_value=1.0, value=default_g, step=5.0)
            with col_preview:
                factor = qty / 100.0
                cal = row["calories_per_100g"] * factor
                pro = row["protein_per_100g"] * factor
                carb = row["carbs_per_100g"] * factor
                fat = row["fat_per_100g"] * factor
                st.markdown(f"""**Estimated macros:**
- Calories: **{cal:.0f} kcal**
- Protein: **{pro:.1f}g**
- Carbs: {carb:.1f}g
- Fat: {fat:.1f}g""")

            if st.button("Add to Log", type="primary", key="btn_db"):
                new = pd.DataFrame([{
                    "date": today, "meal": meal, "food_name": selected,
                    "calories": round(cal, 1), "protein_g": round(pro, 1),
                    "carbs_g": round(carb, 1), "fat_g": round(fat, 1),
                    "quantity": qty, "unit": serving_label, "notes": "",
                }])
                df_log = pd.concat([df_log, new], ignore_index=True)
                save_nutrition_log(df_log)
                st.success(f"Added: {selected}")
                st.rerun()

with tab_custom:
    st.markdown(
        "Add a meal you've eaten. Fill in the macros (estimate from a delivery app, packaging, or restaurant). "
        "Checking **Save to My Foods** will store it permanently in the database so you can reuse it anytime."
    )

    col_left, col_right = st.columns(2)
    with col_left:
        c_name = st.text_input("Meal / Food Name", placeholder="e.g. Pad Kra Pao from BKK delivery")
        c_meal = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout", "Post-workout"], key="custom_meal")
        existing_categories = sorted(df_food["category"].dropna().unique().tolist()) if not df_food.empty else []
        category_options = ["My Foods"] + [c for c in existing_categories if c != "My Foods"] + ["Other"]
        c_category = st.selectbox("Category (for database)", category_options)
        c_cal = st.number_input("Calories (kcal)", min_value=0, value=None, placeholder="0", step=10, key="c_cal")

    with col_right:
        c_pro = st.number_input("Protein (g)", min_value=0.0, value=None, placeholder="0", step=1.0, key="c_pro")
        c_carb = st.number_input("Carbs (g)", min_value=0.0, value=None, placeholder="0", step=1.0, key="c_carb")
        c_fat = st.number_input("Fat (g)", min_value=0.0, value=None, placeholder="0", step=1.0, key="c_fat")
        c_serving_g = st.number_input(
            "Serving size (g) — used for database scaling",
            min_value=1.0, value=100.0, step=10.0,
            help="The weight of one serving in grams. If you don't know, leave at 100.",
        )
        c_serving_name = st.text_input(
            "Serving label",
            value="g (1 serving)",
            help="How the serving is shown, e.g. 'g (1 plate)', '1 cup', '1 piece'",
        )

    c_notes = st.text_input("Notes (optional)", key="c_notes")
    save_to_db = st.checkbox(
        "Save to My Foods database (reuse this meal anytime)",
        value=True,
        help="If checked, this food is saved permanently and will appear in the 'Add from Database' tab.",
    )

    if st.button("Add to Today's Log", type="primary", key="btn_custom"):
        _c_cal = c_cal or 0
        _c_pro = c_pro or 0.0
        _c_carb = c_carb or 0.0
        _c_fat = c_fat or 0.0
        if not c_name:
            st.error("Please enter a meal name.")
        elif _c_cal <= 0:
            st.error("Please enter the calories.")
        else:
            # Always log to today
            new = pd.DataFrame([{
                "date": today, "meal": c_meal, "food_name": c_name,
                "calories": _c_cal, "protein_g": _c_pro, "carbs_g": _c_carb, "fat_g": _c_fat,
                "quantity": c_serving_g, "unit": c_serving_name, "notes": c_notes,
            }])
            df_log = pd.concat([df_log, new], ignore_index=True)
            save_nutrition_log(df_log)

            if save_to_db:
                save_food_to_db(
                    food_name=c_name,
                    category=c_category,
                    calories=_c_cal,
                    protein=_c_pro,
                    carbs=_c_carb,
                    fat=_c_fat,
                    serving_g=c_serving_g,
                    serving_name=c_serving_name,
                )
                st.success(f"Added to today's log and saved **{c_name}** to your food database.")
            else:
                st.success(f"Added to today's log: {c_name}")
            st.rerun()

with tab_myfoods:
    st.markdown("Foods you've saved to the database. You can delete entries here.")
    df_food_live = load_food_db()
    my_foods = df_food_live[df_food_live["category"] == "My Foods"] if not df_food_live.empty else pd.DataFrame()

    if my_foods.empty:
        st.info("No custom foods saved yet. Use 'Add New Meal' with 'Save to My Foods' checked.")
    else:
        for _, row in my_foods.iterrows():
            ca, cb, cc = st.columns([3, 3, 1])
            with ca:
                st.write(f"**{row['food_name']}**")
                st.caption(f"Serving: {row['serving_size_g']}g ({row['serving_name']})")
            with cb:
                sv = row['serving_size_g'] / 100.0
                st.write(
                    f"{row['calories_per_100g']*sv:.0f} kcal  |  "
                    f"P: {row['protein_per_100g']*sv:.0f}g  |  "
                    f"C: {row['carbs_per_100g']*sv:.0f}g  |  "
                    f"F: {row['fat_per_100g']*sv:.0f}g  (per serving)"
                )
            with cc:
                if st.button("Delete", key=f"delfood_{row['food_name']}"):
                    df_food_live = df_food_live[df_food_live["food_name"] != row["food_name"]]
                    df_food_live.to_csv(
                        Path(__file__).parent.parent / "data" / "food_database.csv", index=False
                    )
                    st.success(f"Removed {row['food_name']}")
                    st.rerun()

st.divider()

# --- Today's log ---
st.subheader(f"Today's Log — {today.strftime('%A, %B %d')}")
today_log = df_log[df_log["date"] == today].reset_index()

if today_log.empty:
    st.info("Nothing logged yet. Add your first meal above.")
else:
    for meal_type in ["Breakfast", "Lunch", "Dinner", "Pre-workout", "Post-workout", "Snack"]:
        entries = today_log[today_log["meal"] == meal_type]
        if entries.empty:
            continue
        meal_cal = entries["calories"].sum()
        meal_pro = entries["protein_g"].sum()
        with st.expander(f"**{meal_type}** — {meal_cal:.0f} kcal | {meal_pro:.0f}g protein", expanded=True):
            for _, row in entries.iterrows():
                ca, cb, cc = st.columns([3, 3, 1])
                with ca:
                    st.write(f"**{row['food_name']}** ({row['quantity']} {row['unit']})")
                with cb:
                    st.write(f"{row['calories']:.0f} kcal  |  P: {row['protein_g']:.0f}g  |  C: {row['carbs_g']:.0f}g  |  F: {row['fat_g']:.0f}g")
                with cc:
                    if st.button("✕", key=f"del_{row['index']}_{meal_type}"):
                        df_log = df_log.drop(index=row["index"])
                        df_log = df_log.reset_index(drop=True)
                        save_nutrition_log(df_log)
                        st.rerun()

st.divider()

# --- Past days viewer ---
st.subheader("Past Days")
all_dates = sorted(df_log["date"].unique(), reverse=True)
past_dates = [d for d in all_dates if d != today]

if past_dates:
    sel_date = st.selectbox("View date", past_dates, format_func=lambda d: d.strftime("%A, %B %d %Y"))
    past = df_log[df_log["date"] == sel_date]
    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.metric("Calories", f"{past['calories'].sum():.0f}", f"Target: {TARGETS['calories']}")
    pc2.metric("Protein", f"{past['protein_g'].sum():.0f}g", f"Goal: {pro_target}g | Min: {pro_min}g")
    pc3.metric("Carbs", f"{past['carbs_g'].sum():.0f}g")
    pc4.metric("Fat", f"{past['fat_g'].sum():.0f}g")
    st.dataframe(
        past[["meal", "food_name", "quantity", "unit", "calories", "protein_g", "carbs_g", "fat_g"]].reset_index(drop=True),
        use_container_width=True,
    )
else:
    st.info("Log a few days to see history here.")
