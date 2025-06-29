import os
import pandas as pd
import json

# Only allow these plants (ensure these match your mapping.json keys)
ALLOWED_PLANTS = {f"plant_{i}" for i in range(1, 8)}

def load_mapping():
    with open('config/mapping.json', 'r') as f:
        return json.load(f)

def standardise_shifts(df):
    shift_map = {'1': 'A', '2': 'B', '3': 'C', 1: 'A', 2: 'B', 3: 'C', 'A': 'A', 'B': 'B', 'C': 'C'}
    if 'shift' in df.columns:
        df['shift'] = df['shift'].astype(str).map(shift_map).fillna(df['shift'])
    return df

def process_file(file_name, raw_data_path='data/raw', processed_data_path='data/processed'):
    mapping = load_mapping()
    # Extract plant by filename (assume: plant_X.xlsx)
    base_name = os.path.splitext(file_name)[0].lower()
    if base_name not in mapping or base_name not in ALLOWED_PLANTS:
        raise ValueError(f"Unknown or not-allowed plant: {base_name}. Allowed: {', '.join(sorted(ALLOWED_PLANTS))}")

    # Read and clean data
    df = pd.read_excel(os.path.join(raw_data_path, file_name))
    df = df.rename(columns={k: v for k, v in mapping[base_name].items() if k in df.columns})
    # Lowercase columns just in case
    df.columns = [c.lower() for c in df.columns]
    # Add day of week if not present
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.day_name()
    df = standardise_shifts(df)

    required_cols = {'date', 'shift', 'bottles_produced', 'defect_count', 'downtime', 'day_of_week'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in file {file_name}: {missing}")

    df.to_csv(os.path.join(processed_data_path, f"{base_name}_clean.csv"), index=False)

def process_all_files(raw_data_path='data/raw', processed_data_path='data/processed'):
    processed_count = 0
    for file in os.listdir(raw_data_path):
        if file.lower().endswith('.xlsx'):
            base_name = os.path.splitext(file)[0].lower()
            if base_name in ALLOWED_PLANTS:
                process_file(file, raw_data_path, processed_data_path)
                processed_count += 1
    return processed_count
