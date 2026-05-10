import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

from config import TARGETS, USER
from utils.data import load_nutrition_log, load_workout_log, load_weight_log, save_weight_log
from utils.auth import require_login

st.set_page_config(page_title="Progress", page_icon="📈", layout="wide")
require_login()
st.title("Progress & Analytics")

today = date.today()
df_nutrition = load_nutrition_log()
df_workout = load_workout_log()
df_weight = load_weight_log()

CHART_STYLE = dict(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="#fafafa",
    xaxis=dict(gridcolor="#262730"),
    yaxis=dict(gridcolor="#262730"),
)

# =============================================================
# BODY WEIGHT
# =============================================================
st.subheader("Body Weight")

col_input, col_chart = st.columns([1, 2])

with col_input:
    st.markdown("**Log today's weight**")
    today_weight_entry = df_weight[df_weight["date"] == today]
    default_w = float(today_weight_entry["weight_kg"].values[0]) if not today_weight_entry.empty else USER["weight_kg"]
    new_weight = st.number_input("Weight (kg)", min_value=40.0, max_value=150.0, value=default_w, step=0.1)
    new_bf = st.number_input("Body fat % (optional estimate)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
    w_notes = st.text_input("Note", placeholder="Fasted, post-meal, bloated...")

    if st.button("Log Weight", type="primary"):
        df_weight = df_weight[df_weight["date"] != today]
        new_row = pd.DataFrame([{
            "date": today,
            "weight_kg": new_weight,
            "body_fat_pct": new_bf if new_bf > 0 else None,
            "notes": w_notes,
        }])
        df_weight = pd.concat([df_weight, new_row], ignore_index=True)
        save_weight_log(df_weight)
        st.success(f"Logged {new_weight} kg")
        st.rerun()

    if not df_weight.empty:
        start = USER["start_weight_kg"]
        current = float(df_weight.sort_values("date").iloc[-1]["weight_kg"])
        st.metric("Change from start", f"{current - start:+.1f} kg", f"Start: {start} kg")

with col_chart:
    if not df_weight.empty and len(df_weight) > 0:
        dw = df_weight.sort_values("date")
        fig_w = px.line(dw, x="date", y="weight_kg", title="Body Weight Over Time", markers=True,
                        color_discrete_sequence=["#4fa3e0"])
        fig_w.add_hline(y=USER["start_weight_kg"], line_dash="dash", line_color="#a3e04f",
                        annotation_text=f"Start: {USER['start_weight_kg']}kg")
        fig_w.update_layout(**CHART_STYLE, title_font_size=14)
        st.plotly_chart(fig_w, use_container_width=True)
    else:
        st.info("Log your weight daily to see progress here.")

st.divider()

# =============================================================
# NUTRITION TRENDS
# =============================================================
st.subheader("Nutrition Trends")

if df_nutrition.empty:
    st.info("No nutrition data yet. Start logging meals in the Nutrition tab.")
else:
    df_nutrition["date"] = pd.to_datetime(df_nutrition["date"]).dt.date
    daily = df_nutrition.groupby("date").agg(
        calories=("calories", "sum"),
        protein_g=("protein_g", "sum"),
        carbs_g=("carbs_g", "sum"),
        fat_g=("fat_g", "sum"),
    ).reset_index()

    period = st.radio("Period", ["Last 7 days", "Last 14 days", "Last 30 days"], horizontal=True)
    days_map = {"Last 7 days": 7, "Last 14 days": 14, "Last 30 days": 30}
    cutoff = today - timedelta(days=days_map[period])
    plot_data = daily[daily["date"] >= cutoff].copy()

    if plot_data.empty:
        st.info(f"No data in the last {days_map[period]} days.")
    else:
        col_cal, col_pro = st.columns(2)

        with col_cal:
            fig_cal = go.Figure()
            fig_cal.add_trace(go.Bar(
                x=plot_data["date"], y=plot_data["calories"],
                name="Calories", marker_color="#4fa3e0",
            ))
            fig_cal.add_hline(y=TARGETS["calories"], line_dash="dash", line_color="#a3e04f",
                              annotation_text=f"Target: {TARGETS['calories']} kcal")
            fig_cal.update_layout(**CHART_STYLE, title="Daily Calories", title_font_size=14)
            st.plotly_chart(fig_cal, use_container_width=True)

        with col_pro:
            fig_pro = go.Figure()
            fig_pro.add_trace(go.Bar(
                x=plot_data["date"], y=plot_data["protein_g"],
                name="Protein", marker_color="#a3e04f",
            ))
            fig_pro.add_hline(y=TARGETS["protein_g"], line_dash="dash", line_color="#e0a34f",
                              annotation_text=f"Target: {TARGETS['protein_g']}g")
            fig_pro.update_layout(**CHART_STYLE, title="Daily Protein", title_font_size=14)
            st.plotly_chart(fig_pro, use_container_width=True)

        # Adherence stats
        pro_min = TARGETS["protein_min_g"]
        pro_goal = TARGETS["protein_g"]
        cal_ok = plot_data["calories"].between(TARGETS["calories"] - 250, TARGETS["calories"] + 250).mean() * 100
        pro_ok = (plot_data["protein_g"] >= pro_min).mean() * 100
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Avg Calories", f"{plot_data['calories'].mean():.0f} kcal")
        s2.metric("Avg Protein", f"{plot_data['protein_g'].mean():.0f}g", f"Range: {pro_min}–{pro_goal}g")
        s3.metric("Calorie Adherence", f"{cal_ok:.0f}%", help="Days within ±250 kcal of target")
        s4.metric("Protein Adherence", f"{pro_ok:.0f}%", help=f"Days hitting ≥{pro_min}g (floor)")

st.divider()

# =============================================================
# PERSONAL RECORDS & EXERCISE TRENDS
# =============================================================
st.subheader("Personal Records")

if df_workout.empty:
    st.info("No workout data yet. Start logging in the Workout tab.")
else:
    df_w = df_workout.copy()
    df_w["reps_n"] = pd.to_numeric(df_w["reps"], errors="coerce")
    df_w["weight_kg"] = pd.to_numeric(df_w["weight_kg"], errors="coerce").fillna(0.0)

    # Epley estimated 1RM
    df_w["e1rm"] = df_w.apply(
        lambda r: r["weight_kg"] * (1 + r["reps_n"] / 30)
        if pd.notna(r["reps_n"]) and r["reps_n"] > 0 and r["weight_kg"] > 0 else 0,
        axis=1,
    )

    weighted_exercises = df_w[df_w["weight_kg"] > 0]
    if not weighted_exercises.empty:
        pr_idx = weighted_exercises.groupby("exercise_name")["e1rm"].idxmax()
        prs = weighted_exercises.loc[pr_idx][["exercise_name", "reps", "weight_kg", "e1rm", "date"]].copy()
        prs.columns = ["Exercise", "Reps", "Weight (kg)", "Est. 1RM (kg)", "Date"]
        prs["Est. 1RM (kg)"] = prs["Est. 1RM (kg)"].round(1)
        prs = prs.sort_values("Weight (kg)", ascending=False).reset_index(drop=True)
        st.dataframe(prs, use_container_width=True, hide_index=True)
    else:
        st.info("No weighted exercises logged yet.")

    st.subheader("Exercise Trend")
    exercise_options = sorted(df_w[df_w["weight_kg"] > 0]["exercise_name"].unique().tolist())
    if exercise_options:
        sel_ex = st.selectbox("Select exercise to view", exercise_options)
        ex_data = df_w[(df_w["exercise_name"] == sel_ex) & (df_w["weight_kg"] > 0)].copy()
        ex_data["date"] = pd.to_datetime(ex_data["date"])
        daily_max = ex_data.groupby("date")["weight_kg"].max().reset_index()

        fig_ex = px.line(
            daily_max, x="date", y="weight_kg",
            title=f"{sel_ex} — Max Weight Per Session",
            markers=True, color_discrete_sequence=["#e07a4f"],
        )
        fig_ex.update_layout(**CHART_STYLE, title_font_size=14)
        st.plotly_chart(fig_ex, use_container_width=True)

        # Also show volume (sets × reps × weight)
        ex_data["volume"] = ex_data["reps_n"] * ex_data["weight_kg"]
        daily_vol = ex_data.groupby("date")["volume"].sum().reset_index()
        fig_vol = px.bar(
            daily_vol, x="date", y="volume",
            title=f"{sel_ex} — Total Volume Per Session (reps × kg)",
            color_discrete_sequence=["#a34fe0"],
        )
        fig_vol.update_layout(**CHART_STYLE, title_font_size=14)
        st.plotly_chart(fig_vol, use_container_width=True)

st.divider()

# =============================================================
# WEEKLY VOLUME BREAKDOWN
# =============================================================
st.subheader("Weekly Training Volume by Muscle Group")

if not df_workout.empty and not df_w[df_w["weight_kg"] > 0].empty:
    from config import WORKOUTS as WORKOUT_CONFIG

    # Build exercise -> muscle map
    muscle_map = {}
    for exercises in WORKOUT_CONFIG.values():
        for ex in exercises:
            muscle_map[ex["name"]] = ex.get("muscle", "Other")

    df_w["muscle"] = df_w["exercise_name"].map(muscle_map).fillna("Other")
    df_w["week"] = pd.to_datetime(df_w["date"]).dt.isocalendar().week.astype(str) + "-" + pd.to_datetime(df_w["date"]).dt.year.astype(str)
    df_w["volume"] = df_w["reps_n"].fillna(0) * df_w["weight_kg"]

    weekly_muscle = df_w.groupby(["week", "muscle"])["volume"].sum().reset_index()
    if not weekly_muscle.empty:
        fig_muscle = px.bar(
            weekly_muscle, x="week", y="volume", color="muscle",
            title="Weekly Volume by Muscle Group",
            barmode="stack",
        )
        fig_muscle.update_layout(**CHART_STYLE, title_font_size=14)
        st.plotly_chart(fig_muscle, use_container_width=True)
else:
    st.info("Log a few workouts to see volume breakdown here.")
