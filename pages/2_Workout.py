import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import date

from config import DAY_TO_WORKOUT, WORKOUTS
from utils.data import load_workout_log, save_workout_log, get_last_workout_data
from utils.auth import require_login

st.set_page_config(page_title="Workout", page_icon="🏋️", layout="wide")
require_login()
st.title("Workout Tracker")

today = date.today()
day_idx = today.weekday()
default_workout = DAY_TO_WORKOUT.get(day_idx, "Rest")

df_log = load_workout_log()

col_sel, col_date = st.columns([3, 1])
with col_sel:
    all_workouts = [k for k, v in WORKOUTS.items() if v]
    default_idx = all_workouts.index(default_workout) if default_workout in all_workouts else 0
    selected_workout = st.selectbox("Select Workout", all_workouts, index=default_idx)
with col_date:
    log_date = st.date_input("Date", value=today, max_value=today)

exercises = WORKOUTS.get(selected_workout, [])

if not exercises:
    st.info("Rest day. Enjoy the recovery.")
    st.stop()

existing = df_log[(df_log["date"] == log_date) & (df_log["workout_name"] == selected_workout)]
if not existing.empty:
    logged = existing["exercise_name"].unique()
    st.caption(f"Already logged: {', '.join(logged)}")

st.divider()

for ex in exercises:
    ex_name = ex["name"]
    last_data = get_last_workout_data(ex_name, selected_workout)
    has_prev = not last_data.empty

    with st.expander(
        f"**{ex_name}** — {ex['muscle']} · {ex['target_sets']}×{ex['target_reps']} · Rest {ex['rest']}",
        expanded=True,
    ):
        # Previous session as a single compact line
        if has_prev:
            prev_date = last_data["date"].max()
            prev_parts = []
            for _, r in last_data.iterrows():
                w = "BW" if r["weight_kg"] == 0 else f"{r['weight_kg']}kg"
                prev_parts.append(f"S{int(r['set_number'])}: {int(r['reps'])}r@{w}")
            st.caption(f"Last ({prev_date}): {'  ·  '.join(prev_parts)}")

        num_sets = st.number_input(
            "Sets", min_value=1, max_value=10,
            value=int(ex["target_sets"]),
            key=f"nsets_{ex_name}",
            label_visibility="collapsed",
        )

        set_cols = st.columns(num_sets)
        set_inputs = []

        for s in range(num_sets):
            prev_set = last_data[last_data["set_number"] == s + 1] if has_prev else pd.DataFrame()
            prev_reps = int(prev_set["reps"].values[0]) if not prev_set.empty and prev_set["reps"].values[0] > 0 else None
            prev_weight = float(prev_set["weight_kg"].values[0]) if not prev_set.empty and prev_set["weight_kg"].values[0] > 0 else None

            with set_cols[s]:
                st.markdown(f"**S{s+1}**")
                reps = st.number_input(
                    "Reps", min_value=0, value=prev_reps,
                    placeholder="reps",
                    key=f"r_{ex_name}_{s}",
                    label_visibility="collapsed",
                )
                weight = st.number_input(
                    "kg (0=BW)", min_value=0.0, value=prev_weight,
                    placeholder="kg",
                    step=0.5,
                    key=f"w_{ex_name}_{s}",
                    label_visibility="collapsed",
                )

                # Progressive overload indicator
                if has_prev and (prev_reps is not None or prev_weight is not None):
                    curr_r = reps or 0
                    curr_w = weight or 0
                    p_r = prev_reps or 0
                    p_w = prev_weight or 0
                    if curr_w > p_w or (curr_w == p_w and curr_r > p_r):
                        st.caption("↑ PR")
                    elif curr_w == p_w and curr_r == p_r and curr_r > 0:
                        st.caption("= same")
                    elif curr_r > 0:
                        st.caption("↓")

            set_inputs.append({"set": s + 1, "reps": reps or 0, "weight": weight or 0.0})

        if st.button(f"Save {ex_name}", key=f"save_{ex_name}", type="primary"):
            rows_to_save = [
                {
                    "date": log_date,
                    "workout_name": selected_workout,
                    "exercise_name": ex_name,
                    "set_number": s["set"],
                    "reps": s["reps"],
                    "weight_kg": s["weight"],
                    "notes": "",
                }
                for s in set_inputs if s["reps"] > 0
            ]
            if rows_to_save:
                df_log = df_log[~(
                    (df_log["date"] == log_date) &
                    (df_log["workout_name"] == selected_workout) &
                    (df_log["exercise_name"] == ex_name)
                )]
                df_log = pd.concat([df_log, pd.DataFrame(rows_to_save)], ignore_index=True)
                save_workout_log(df_log)
                st.success(f"Saved!")
                st.rerun()
            else:
                st.warning("Enter at least 1 rep to save.")

st.divider()

# Past sessions
st.subheader("Past Sessions")
df_log = load_workout_log()

if df_log.empty:
    st.info("No logs yet.")
else:
    past_dates = sorted(df_log["date"].unique(), reverse=True)[:20]
    sel_past = st.selectbox(
        "View session",
        past_dates,
        format_func=lambda d: d.strftime("%A, %B %d %Y"),
    )
    past_session = df_log[df_log["date"] == sel_past]
    for workout in past_session["workout_name"].unique():
        st.markdown(f"**{workout}**")
        wdata = past_session[past_session["workout_name"] == workout]
        for ex in wdata["exercise_name"].unique():
            ex_data = wdata[wdata["exercise_name"] == ex].sort_values("set_number")
            sets_str = "  ·  ".join(
                f"S{int(r['set_number'])}: {int(r['reps'])}r @ {'BW' if r['weight_kg']==0 else str(r['weight_kg'])+'kg'}"
                for _, r in ex_data.iterrows()
            )
            st.markdown(f"— *{ex}*: {sets_str}")
