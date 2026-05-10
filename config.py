USER = {
    "name": "You",
    "age": 24,
    "weight_kg": 66.0,
    "height_cm": 166,
    "sex": "male",
    "start_weight_kg": 66.0,
}

# Daily targets (recomp: slight deficit, high protein)
TARGETS = {
    "calories": 2150,
    "protein_g": 120,       # goal
    "protein_min_g": 110,   # acceptable floor (1.67g/kg)
    "carbs_g": 270,
    "fat_g": 60,
}

DAY_TO_WORKOUT = {
    0: "Upper A (Push) — GYM",
    1: "Lower A (Legs) — GYM",
    2: "Cardio — Run",
    3: "Upper B (Pull) — HOME",
    4: "Lower B + Core — HOME",
    5: "Badminton",
    6: "Rest",
}

WORKOUTS = {
    "Upper A (Push) — GYM": [
        {
            "name": "Incline Barbell Bench Press",
            "target_sets": 4, "target_reps": "6-10", "rest": "2 min",
            "notes": "30-45° incline. Don't flare elbows. Priority compound.",
            "muscle": "Upper Chest / Shoulders",
        },
        {
            "name": "Flat DB Bench Press",
            "target_sets": 3, "target_reps": "10-12", "rest": "90 sec",
            "notes": "Full stretch at bottom. Squeeze at top.",
            "muscle": "Chest",
        },
        {
            "name": "Cable Lateral Raise (Single Arm)",
            "target_sets": 4, "target_reps": "15-20", "rest": "60 sec",
            "notes": "Light weight. Feel the delt. Priority for shoulder width.",
            "muscle": "Side Delts",
        },
        {
            "name": "Seated DB Shoulder Press",
            "target_sets": 3, "target_reps": "10-12", "rest": "90 sec",
            "notes": "Don't lock out at top. Keep tension on delts.",
            "muscle": "Shoulders",
        },
        {
            "name": "Cable Chest Fly / Pec Deck",
            "target_sets": 3, "target_reps": "12-15", "rest": "60 sec",
            "notes": "Slow negative. Squeeze hard at centre.",
            "muscle": "Chest",
        },
        {
            "name": "Tricep Rope Pushdown",
            "target_sets": 3, "target_reps": "12-15", "rest": "60 sec",
            "notes": "Elbows pinned to sides. Flare rope at bottom.",
            "muscle": "Triceps",
        },
        {
            "name": "Overhead Tricep Extension",
            "target_sets": 2, "target_reps": "12-15", "rest": "60 sec",
            "notes": "Long head of tricep. Makes arms look bigger.",
            "muscle": "Triceps",
        },
        {
            "name": "Face Pull (Cable)",
            "target_sets": 3, "target_reps": "15-20", "rest": "60 sec",
            "notes": "ADDED: Rear delt balance. Pull to forehead, elbows high. Keeps shoulders healthy.",
            "muscle": "Rear Delts",
        },
    ],
    "Lower A (Legs) — GYM": [
        {
            "name": "Barbell Back Squat",
            "target_sets": 4, "target_reps": "6-10", "rest": "2 min",
            "notes": "Hip-width stance. Thighs parallel at bottom. Chest tall.",
            "muscle": "Quads / Glutes",
        },
        {
            "name": "Romanian Deadlift",
            "target_sets": 4, "target_reps": "10-12", "rest": "90 sec",
            "notes": "Hinge at hips. Soft knee. Feel hamstring stretch. Priority for APT correction.",
            "muscle": "Hamstrings / Glutes",
        },
        {
            "name": "Leg Press",
            "target_sets": 3, "target_reps": "12-15", "rest": "90 sec",
            "notes": "Feet higher on platform for more glute. Don't lock knees at top.",
            "muscle": "Quads / Glutes",
        },
        {
            "name": "Walking Lunges (DB)",
            "target_sets": 3, "target_reps": "12 each leg", "rest": "90 sec",
            "notes": "Long stride for more glute activation.",
            "muscle": "Glutes / Quads",
        },
        {
            "name": "Leg Curl Machine",
            "target_sets": 3, "target_reps": "12-15", "rest": "60 sec",
            "notes": "3 sec slow negative. Don't skip this.",
            "muscle": "Hamstrings",
        },
        {
            "name": "Hip Thrust (Barbell)",
            "target_sets": 3, "target_reps": "15", "rest": "60 sec",
            "notes": "Drive through heels. Squeeze hard at top for 1 sec.",
            "muscle": "Glutes",
        },
        {
            "name": "Calf Raise",
            "target_sets": 4, "target_reps": "15-20", "rest": "45 sec",
            "notes": "Full range all the way down and up. Go slow.",
            "muscle": "Calves",
        },
    ],
    "Upper B (Pull) — HOME": [
        {
            "name": "Pull-ups (Wide Grip)",
            "target_sets": 4, "target_reps": "max (aim 6-10)", "rest": "2 min",
            "notes": "PRIORITY #1. Full hang at bottom. Drives lat width = V-taper.",
            "muscle": "Lats / Upper Back",
        },
        {
            "name": "Chin-ups",
            "target_sets": 2, "target_reps": "max", "rest": "90 sec",
            "notes": "Supinated grip. Bicep emphasis. Do after pull-ups.",
            "muscle": "Lats / Biceps",
        },
        {
            "name": "DB Bent-over Row",
            "target_sets": 4, "target_reps": "10-12", "rest": "90 sec",
            "notes": "Hinge 45°. Drive elbow back and up. Squeeze at top.",
            "muscle": "Mid-Back / Lats",
        },
        {
            "name": "DB Rear Delt Fly",
            "target_sets": 3, "target_reps": "15-20", "rest": "60 sec",
            "notes": "Bent over. Light weight. Feel rear delt contract. Key for 3D shoulders.",
            "muscle": "Rear Delts",
        },
        {
            "name": "Prone Y-T-W (Floor)",
            "target_sets": 3, "target_reps": "10 each position", "rest": "60 sec",
            "notes": "Lie face down. Y=arms overhead, T=arms to sides, W=bent elbows. Light or no weight.",
            "muscle": "Upper Back / Rear Delts",
        },
        {
            "name": "DB Bicep Curl",
            "target_sets": 3, "target_reps": "10-12", "rest": "60 sec",
            "notes": "Supinate at top. No swinging.",
            "muscle": "Biceps",
        },
        {
            "name": "Hammer Curl",
            "target_sets": 2, "target_reps": "12-15", "rest": "60 sec",
            "notes": "Neutral grip. Builds brachialis — arm thickness.",
            "muscle": "Biceps / Brachialis",
        },
        {
            "name": "Floor DB Pullover",
            "target_sets": 3, "target_reps": "12-15", "rest": "60 sec",
            "notes": "Lie on floor. Arms extend over head. Lat stretch + serratus. Bench-free alternative.",
            "muscle": "Lats / Serratus",
        },
    ],
    "Lower B + Core — HOME": [
        {
            "name": "Bulgarian Split Squat (DB)",
            "target_sets": 4, "target_reps": "10 each leg", "rest": "2 min",
            "notes": "Rear foot on chair. Long front stride. Hardest home leg exercise. Worth every rep.",
            "muscle": "Quads / Glutes",
        },
        {
            "name": "DB Hip Thrust",
            "target_sets": 4, "target_reps": "15", "rest": "90 sec",
            "notes": "Shoulders on sofa/bed edge. DB on hips. Drive through heels. Squeeze at top.",
            "muscle": "Glutes",
        },
        {
            "name": "DB Single-Leg Romanian Deadlift",
            "target_sets": 3, "target_reps": "10 each leg", "rest": "90 sec",
            "notes": "Hold DB in opposite hand to working leg. Go slow for balance.",
            "muscle": "Hamstrings / Glutes",
        },
        {
            "name": "DB Sumo Squat",
            "target_sets": 3, "target_reps": "15", "rest": "75 sec",
            "notes": "Wide stance. Toes out. Hold one heavy DB at chest. Inner thigh and glute focus.",
            "muscle": "Inner Thigh / Glutes",
        },
        {
            "name": "Dead Bug",
            "target_sets": 3, "target_reps": "10 each side", "rest": "30 sec",
            "notes": "Lower back FLAT on floor at all times. Best core stability exercise.",
            "muscle": "Core (Anti-extension)",
        },
        {
            "name": "Russian Twist",
            "target_sets": 3, "target_reps": "20", "rest": "30 sec",
            "notes": "Bodyweight only — do NOT add weight. Keeps waist slim.",
            "muscle": "Obliques",
        },
        {
            "name": "Bicycle Crunch",
            "target_sets": 3, "target_reps": "20", "rest": "30 sec",
            "notes": "Slow and controlled. Not a race.",
            "muscle": "Abs / Obliques",
        },
        {
            "name": "Lying Leg Raise",
            "target_sets": 3, "target_reps": "15", "rest": "30 sec",
            "notes": "Lower back stays on floor. Bend knees slightly if needed.",
            "muscle": "Lower Abs",
        },
        {
            "name": "Side Plank",
            "target_sets": 3, "target_reps": "30 sec each side", "rest": "30 sec",
            "notes": "Stack feet or stagger. Keep hips up.",
            "muscle": "Obliques / Core",
        },
        {
            "name": "Twist Side Hanging Leg Raise",
            "target_sets": 3, "target_reps": "10 each side", "rest": "30 sec",
            "notes": "Using hanging bar. Twist hips toward each side at top.",
            "muscle": "Obliques / Lower Abs",
        },
    ],
    "Cardio — Run": [
        {
            "name": "Zone 2 Run",
            "target_sets": 1, "target_reps": "5-10 km", "rest": "—",
            "notes": "Easy pace — you can hold a conversation. HR ~120-140 bpm. Fat burning zone.",
            "muscle": "Cardio / Fat Loss",
        },
    ],
    "Badminton": [
        {
            "name": "Badminton Session",
            "target_sets": 1, "target_reps": "60-90 min", "rest": "—",
            "notes": "Active recovery. Have fun — don't think about metrics.",
            "muscle": "Full Body",
        },
    ],
    "Rest": [],
}
