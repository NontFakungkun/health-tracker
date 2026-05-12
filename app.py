import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from datetime import date
import random

from config import USER, TARGETS, DAY_TO_WORKOUT, WORKOUTS
from utils.data import get_today_nutrition, load_weight_log

st.set_page_config(
    page_title="Fitness Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stMetricDelta"] svg { display: none; }
</style>
""", unsafe_allow_html=True)

today = date.today()
day_idx = today.weekday()
today_workout = DAY_TO_WORKOUT.get(day_idx, "Rest")

st.title("Fitness Tracker")
st.markdown(f"**{today.strftime('%A, %B %d %Y')}**  —  Today: `{today_workout}`")
st.divider()

# --- Daily snapshot ---
nutrition = get_today_nutrition()
cal_rem = TARGETS["calories"] - nutrition["calories"]
pro_target = TARGETS["protein_g"]
pro_min = TARGETS["protein_min_g"]
pro_rem = pro_target - nutrition["protein_g"]

weight_log = load_weight_log()
if not weight_log.empty:
    current_weight = float(weight_log.sort_values("date").iloc[-1]["weight_kg"])
    weight_delta = current_weight - USER["start_weight_kg"]
    weight_label = f"{current_weight:.1f} kg"
    weight_delta_label = f"{weight_delta:+.1f} kg since start"
else:
    weight_label = f"{USER['weight_kg']:.1f} kg"
    weight_delta_label = "Log weight in Progress tab"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Calories Today", f"{nutrition['calories']:.0f} / {TARGETS['calories']}", f"{cal_rem:.0f} remaining")
col2.metric("Protein Today", f"{nutrition['protein_g']:.0f}g / {pro_target}g", f"{pro_rem:.0f}g to goal (min {pro_min}g)")
col3.metric("Body Weight", weight_label, weight_delta_label)
col4.metric("Meals Logged", nutrition["entries"])

st.divider()

# --- Progress bars ---
st.subheader("Today's Targets")
c1, c2 = st.columns(2)
with c1:
    cal_pct = min(nutrition["calories"] / TARGETS["calories"], 1.0)
    st.markdown(f"**Calories** — {nutrition['calories']:.0f} / {TARGETS['calories']} kcal  ({cal_pct*100:.0f}%)")
    st.progress(cal_pct)
with c2:
    pro_pct = min(nutrition["protein_g"] / pro_target, 1.0)
    st.markdown(f"**Protein** — {nutrition['protein_g']:.0f} / {pro_target}g  ({pro_pct*100:.0f}%)  ·  range: {pro_min}–{pro_target}g")
    st.progress(pro_pct)

st.divider()

# --- Today's workout preview ---
st.subheader(f"Today's Workout: {today_workout}")
exercises = WORKOUTS.get(today_workout, [])

if exercises:
    num_cols = min(len(exercises), 3)
    cols = st.columns(num_cols)
    for i, ex in enumerate(exercises):
        with cols[i % num_cols]:
            st.markdown(f"""**{ex['name']}**
- {ex['target_sets']} sets × {ex['target_reps']}
- Rest: {ex['rest']}
- *{ex['muscle']}*
""")
elif today_workout == "Rest":
    st.info("Rest day. Sleep well, eat your protein, and recover — growth happens here.")
else:
    st.info(f"No exercises defined for {today_workout}.")

st.divider()

# --- Target breakdown reference ---
with st.expander("Your Daily Targets Reference"):
    st.markdown(f"""
| Macro | Target | Why |
|-------|--------|-----|
| **Calories** | {TARGETS['calories']} kcal | ~300 kcal deficit from TDEE for recomp |
| **Protein** | {TARGETS['protein_g']}g | 2g/kg — muscle retention + building |
| **Carbs** | {TARGETS['carbs_g']}g | Fuels training, fills the rest |
| **Fat** | {TARGETS['fat_g']}g | Minimum for hormonal health |

**Body recomposition note:** You're in a slight deficit on rest days and near maintenance on heavy training days. That's fine — your body will use stored fat when you're in deficit and still build muscle with sufficient protein and training stimulus.
""")

# --- Daily tip ---
tips = [
    "Protein first — build every meal around your protein source, then add carbs.",
    "Progressive overload is the #1 driver of muscle growth. Log every session.",
    "Sleep 7-9 hours. Growth hormone peaks during deep sleep.",
    "Zone 2 running burns fat without killing recovery. Keep Wednesday easy.",
    "Shoulders are your visual multiplier. Never skip lateral raises.",
    "The V-taper is built with wide lats and a slim waist — not just big shoulders.",
    "Consistency beats perfection. One missed day means nothing. A missed week matters.",
    "Pull-ups are your most important home exercise. Every rep builds the V-taper.",
    "Rear delts are the most underdeveloped muscle in most physiques. Face pulls fix this.",
    "Recomp is slow — trust the process. Changes show in 8-12 weeks.",
    "Your core routine is designed to keep your waist flat. Keep core exercises bodyweight.",
]
tip = tips[today.toordinal() % len(tips)]
st.caption(f"Daily note: {tip}")
