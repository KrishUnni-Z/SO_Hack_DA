import os
import pandas as pd
import json

# Load the mapping.json once (do this at the top of the file)
with open("mapping.json", "r") as f:
    mapping = json.load(f)

PLANT_FILES = set(mapping.keys())

def get_plant_name_from_filename(filename):
    # Assumes plant file format is plant_X.xlsx, not case sensitive
    fname = filename.lower().replace(".xlsx", "")
    for plant in PLANT_FILES:
        if plant.lower() == fname:
            return plant
    return None

def process_file(file_name, raw_data_path='data/raw', processed_data_path='data/processed'):
    plant_name = get_plant_name_from_filename(file_name)
    if plant_name is None:
        # Not a plant file, silently ignore
        print(f"Skipped unknown file: {file_name}")
        return None

    mapping_dict = mapping[plant_name]
    file_path = os.path.join(raw_data_path, file_name)
    df = pd.read_excel(file_path)
    # Make all columns lower case for matching
    df.columns = [c.lower().strip() for c in df.columns]

    # Build a reverse mapping (case-insensitive)
    reverse_map = {k.lower(): v for k, v in mapping_dict.items()}
    new_cols = {}
    for col in df.columns:
        if col in reverse_map:
            new_cols[col] = reverse_map[col]
        else:
            raise ValueError(f"Missing expected column '{col}' in {file_name}")

    df = df.rename(columns=new_cols)
    # Add any additional columns if needed, e.g. day_of_week
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    # Save as clean file
    out_file = os.path.join(processed_data_path, f"{plant_name}_clean.csv")
    df.to_csv(out_file, index=False)
    return plant_name

def process_all_files(raw_data_path='data/raw', processed_data_path='data/processed'):
    all_files = [f for f in os.listdir(raw_data_path) if f.endswith('.xlsx')]
    replaced = []
    for file in all_files:
        plant_name = get_plant_name_from_filename(file)
        if plant_name:
            if os.path.exists(os.path.join(processed_data_path, f"{plant_name}_clean.csv")):
                replaced.append(plant_name)
            process_file(file, raw_data_path, processed_data_path)
    return replaced
