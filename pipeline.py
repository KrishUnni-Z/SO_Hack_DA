import os
import json
import pandas as pd

raw_data_path = 'data/raw'
processed_data_path = 'data/processed'

# Load the mapping.json ONCE at module load
with open('mapping.json', 'r') as f:
    plant_maps = json.load(f)

REQUIRED_COLS = ['date', 'shift', 'bottles_produced', 'defect_count', 'downtime']

def process_file(file_name):
    file_path = os.path.join(raw_data_path, file_name)
    df = pd.read_excel(file_path)
    df.columns = [col.strip() for col in df.columns]

    # Infer plant name from file name
    # Assume: 'plant_3.xlsx' → 'plant_3'
    plant_id = file_name.replace('.xlsx', '').lower()
    if plant_id not in plant_maps:
        raise ValueError(f"Unknown plant: {plant_id}. Add it to mapping.json.")

    # Build a local column mapping, making both sides lower-case for safety
    map_this = {k.lower(): v.lower() for k, v in plant_maps[plant_id].items()}
    # Lower-case the DataFrame columns for robust matching
    df.columns = [col.lower() for col in df.columns]
    df = df.rename(columns=map_this)

    # Check for missing columns
    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(
                f"Missing column: '{col}' in file '{file_name}'.\nColumns present: {list(df.columns)}"
            )

    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    save_name = file_name.replace('.xlsx', '_clean.csv')
    df.to_csv(os.path.join(processed_data_path, save_name), index=False)

def process_all_files():
    for file in os.listdir(raw_data_path):
        if file.endswith('.xlsx'):
            process_file(file)
