import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import date

from config import DAY_TO_WORKOUT, WORKOUTS
from utils.data import load_workout_log, save_workout_log, get_last_workout_data

st.set_page_config(page_title="Workout", page_icon="🏋️", layout="wide")
st.title("Workout Tracker")

today = date.today()
day_idx = today.weekday()
default_workout = DAY_TO_WORKOUT.get(day_idx, "Rest")

df_log = load_workout_log()

# Header controls
col_sel, col_date = st.columns([3, 1])
with col_sel:
    all_workouts = [k for k, v in WORKOUTS.items() if v]
    default_idx = all_workouts.index(default_workout) if default_workout in all_workouts else 0
    selected_workout = st.selectbox("Select Workout", all_workouts, index=default_idx)
with col_date:
    log_date = st.date_input("Date", value=today, max_value=today)

st.divider()

exercises = WORKOUTS.get(selected_workout, [])

if not exercises:
    st.info("Rest day or no exercises defined. Enjoy the recovery.")
    st.stop()

# Check if session already has entries
existing = df_log[(df_log["date"] == log_date) & (df_log["workout_name"] == selected_workout)]
if not existing.empty:
    logged_exs = existing["exercise_name"].unique()
    st.success(f"Session in progress. Already logged: {', '.join(logged_exs)}")

st.subheader(selected_workout)

for ex in exercises:
    ex_name = ex["name"]
    last_data = get_last_workout_data(ex_name, selected_workout)
    has_prev = not last_data.empty

    header = f"**{ex_name}** — {ex['muscle']}  |  Target: {ex['target_sets']} × {ex['target_reps']}  |  Rest: {ex['rest']}"
    with st.expander(header, expanded=True):

        if ex.get("notes"):
            st.caption(f"Cue: {ex['notes']}")

        # Previous session reference
        if has_prev:
            prev_date = last_data["date"].max()
            st.markdown(f"**Previous ({prev_date}):**")
            prev_cols = st.columns(len(last_data))
            for i, (_, r) in enumerate(last_data.iterrows()):
                with prev_cols[i]:
                    w = f"{r['weight_kg']}kg" if r["weight_kg"] > 0 else "BW"
                    st.markdown(f"Set {int(r['set_number'])}: **{int(r['reps'])} reps @ {w}**")
        else:
            st.caption("No previous data — first time logging this exercise.")

        st.markdown("**Log today:**")
        num_sets = st.number_input(
            "Sets", min_value=1, max_value=10,
            value=int(ex["target_sets"]),
            key=f"nsets_{ex_name}",
        )

        set_cols = st.columns(num_sets)
        set_inputs = []
        for s in range(num_sets):
            prev_set = last_data[last_data["set_number"] == s + 1] if has_prev else pd.DataFrame()
            prev_reps = int(prev_set["reps"].values[0]) if not prev_set.empty else 0
            prev_weight = float(prev_set["weight_kg"].values[0]) if not prev_set.empty else 0.0

            with set_cols[s]:
                st.markdown(f"**Set {s+1}**")
                reps = st.number_input("Reps", min_value=0, value=prev_reps, key=f"r_{ex_name}_{s}")
                weight = st.number_input("kg (0=BW)", min_value=0.0, value=prev_weight, step=0.5, key=f"w_{ex_name}_{s}")

                if has_prev and (prev_reps > 0 or prev_weight > 0):
                    if weight > prev_weight or (weight == prev_weight and reps > prev_reps):
                        st.markdown("**↑ Better**")
                    elif weight == prev_weight and reps == prev_reps:
                        st.markdown("= Same")
                    elif reps > 0:
                        st.markdown("↓ Lower")

                set_inputs.append({"set": s + 1, "reps": reps, "weight": weight})

        ex_note = st.text_input("Exercise note", key=f"note_{ex_name}", placeholder="How did it feel?")

        if st.button(f"Save {ex_name}", key=f"save_{ex_name}", type="primary"):
            rows_to_save = [
                {
                    "date": log_date,
                    "workout_name": selected_workout,
                    "exercise_name": ex_name,
                    "set_number": s["set"],
                    "reps": s["reps"],
                    "weight_kg": s["weight"],
                    "notes": ex_note,
                }
                for s in set_inputs if s["reps"] > 0
            ]
            if rows_to_save:
                # Remove existing entries for this exercise on this date
                df_log = df_log[~(
                    (df_log["date"] == log_date) &
                    (df_log["workout_name"] == selected_workout) &
                    (df_log["exercise_name"] == ex_name)
                )]
                df_log = pd.concat([df_log, pd.DataFrame(rows_to_save)], ignore_index=True)
                save_workout_log(df_log)
                st.success(f"Saved {ex_name}!")
                st.rerun()
            else:
                st.warning("Enter at least 1 rep to save.")

st.divider()

# --- Session history ---
st.subheader("Past Sessions")
df_log = load_workout_log()

if df_log.empty:
    st.info("No workout logs yet.")
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
            sets_str = "  |  ".join(
                f"Set {int(r['set_number'])}: {int(r['reps'])} reps @ {'BW' if r['weight_kg'] == 0 else str(r['weight_kg'])+'kg'}"
                for _, r in ex_data.iterrows()
            )
            st.markdown(f"  — *{ex}*: {sets_str}")
            if ex_data["notes"].any():
                note = ex_data["notes"].dropna().iloc[0] if not ex_data["notes"].dropna().empty else ""
                if note:
                    st.caption(f"    Note: {note}")
