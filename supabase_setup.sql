-- Run this in Supabase SQL Editor

create table if not exists nutrition_log (
  id bigint generated always as identity primary key,
  date date, meal text, food_name text,
  calories float, protein_g float, carbs_g float, fat_g float,
  quantity float, unit text, notes text
);

create table if not exists workout_log (
  id bigint generated always as identity primary key,
  date date, workout_name text, exercise_name text,
  set_number int, reps float, weight_kg float, notes text
);

create table if not exists weight_log (
  id bigint generated always as identity primary key,
  date date, weight_kg float, body_fat_pct float, notes text
);

-- Allow read/write with the anon key (auth is handled by Streamlit password)
alter table nutrition_log enable row level security;
alter table workout_log   enable row level security;
alter table weight_log    enable row level security;

create policy "allow all" on nutrition_log for all using (true) with check (true);
create policy "allow all" on workout_log   for all using (true) with check (true);
create policy "allow all" on weight_log    for all using (true) with check (true);
