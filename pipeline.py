# pipeline.py

import os
import pandas as pd
import json

raw_data_path = 'data/raw'
processed_data_path = 'data/processed'
mapping_path = 'config/mapping.json'

os.makedirs(processed_data_path, exist_ok=True)

with open(mapping_path) as f:
    mapping = json.load(f)

def process_file(file_name):
    plant_name = file_name.split('.')[0]
    if plant_name in mapping:
        df = pd.read_excel(os.path.join(raw_data_path, file_name))
        plant_map = mapping[plant_name]
        df = df.rename(columns=plant_map)

        needed_cols = ['date', 'shift', 'bottles_produced', 'defect_count', 'downtime']
        for col in needed_cols:
            if col not in df.columns:
                df[col] = None

        df['date'] = pd.to_datetime(df['date']).dt.date

        if plant_name == 'plant_5':
            df['downtime'] = df['downtime'] * 60

        df['shift'] = df['shift'].astype(str).str.upper().str.strip()
        df['shift'] = df['shift'].apply(lambda x: 'A' if x in ['A', '1'] else ('B' if x in ['B', '2'] else 'C'))

        df[needed_cols].to_csv(os.path.join(processed_data_path, f"{plant_name}_clean.csv"), index=False)

def process_all_files():
    for file in os.listdir(raw_data_path):
        if file.endswith('.xlsx'):
            process_file(file)
