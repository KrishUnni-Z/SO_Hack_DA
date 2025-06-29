import os
import pandas as pd

raw_data_path = 'data/raw'
processed_data_path = 'data/processed'
os.makedirs(raw_data_path, exist_ok=True)
os.makedirs(processed_data_path, exist_ok=True)

def process_file(file_name):
    # Load Excel, basic clean, create day_of_week, save as CSV
    file_path = os.path.join(raw_data_path, file_name)
    df = pd.read_excel(file_path)
    
    # Standardize column names just in case
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    # Ensure columns exist (adjust as needed)
    required = ['date', 'shift', 'bottles_produced', 'defect_count', 'downtime']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Convert date and add day_of_week
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Standardize shift labels (optional)
    df['shift'] = df['shift'].astype(str).str.strip().str.upper().str.replace('SHIFT ', '').str.replace('SHIFT', '')
    shift_map = {'A':'A', 'B':'B', 'C':'C', '1':'A', '2':'B', '3':'C'}
    df['shift'] = df['shift'].replace(shift_map)

    # Save processed
    out_file = file_name.replace('.xlsx', '_clean.csv')
    df.to_csv(os.path.join(processed_data_path, out_file), index=False)

def process_all_files():
    # Process every .xlsx file in raw_data_path
    for file in os.listdir(raw_data_path):
        if file.endswith('.xlsx'):
            process_file(file)
