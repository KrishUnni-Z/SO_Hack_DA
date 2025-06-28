import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def load_processed_data(processed_data_path='data/processed'):
    all_data = []
    for file in os.listdir(processed_data_path):
        if file.endswith('_clean.csv'):
            df = pd.read_csv(os.path.join(processed_data_path, file))
            df['plant'] = file.replace('_clean.csv', '')
            all_data.append(df)
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined['date'] = pd.to_datetime(combined['date'])
        return combined
    return pd.DataFrame()

def filter_data(df):
    plants = df['plant'].unique()
    selected_plants = st.multiselect("Select Plants", plants, default=plants)
    shifts = df['shift'].unique()
    selected_shifts = st.multiselect("Select Shifts", shifts, default=shifts)
    date_range = st.date_input("Select Date Range", [df['date'].min(), df['date'].max()])

    filtered_df = df[
        (df['plant'].isin(selected_plants)) &
        (df['shift'].isin(selected_shifts)) &
        (df['date'] >= pd.to_datetime(date_range[0])) &
        (df['date'] <= pd.to_datetime(date_range[1]))
    ]
    return filtered_df

def show_production_trends(df, smoothing=True):
    grouped = df.groupby('date')['bottles_produced'].sum()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped.index, grouped.values, label='Raw')
    if smoothing:
        smoothed = grouped.rolling(window=7, min_periods=1).mean()
        ax.plot(grouped.index, smoothed.values, linestyle='--', label='7-day Avg')
    ax.set_xlabel('Date', fontsize=8)
    ax.set_ylabel('Bottles Produced', fontsize=8)
    ax.set_title('📈 Production Trend', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    ax.legend(fontsize=7)
    st.pyplot(fig)

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped['date'], grouped['defect_rate'], label='Defect Rate')
    if smoothing:
        smoothed = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        ax.plot(grouped['date'], smoothed, linestyle='--', label='7-day Avg')
    ax.set_xlabel('Date', fontsize=8)
    ax.set_ylabel('Defect Rate (%)', fontsize=8)
    ax.set_title('📉 Defect Rate Trend', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    ax.legend(fontsize=7)
    st.pyplot(fig)

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date')['downtime'].sum()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped.index, grouped.values, label='Downtime')
    if smoothing:
        smoothed = grouped.rolling(window=7, min_periods=1).mean()
        ax.plot(grouped.index, smoothed.values, linestyle='--', label='7-day Avg')
    ax.set_xlabel('Date', fontsize=8)
    ax.set_ylabel('Downtime (mins)', fontsize=8)
    ax.set_title('🕒 Downtime Trend', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    ax.legend(fontsize=7)
    st.pyplot(fig)

def show_defect_vs_production_scatter(df):
    st.subheader("🔎 Defect Count vs. Bottles Produced")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(df['bottles_produced'], df['defect_count'], alpha=0.5)
    ax.set_xlabel('Bottles Produced', fontsize=8)
    ax.set_ylabel('Defect Count', fontsize=8)
    ax.set_title('Defect vs Production Scatter', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    st.pyplot(fig)

def show_shift_breakdown(df):
    st.subheader("📊 Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({
        'bottles_produced': 'sum',
        'defect_count': 'sum'
    }).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(grouped['shift'].astype(str), grouped['Defect %'])
    ax.set_xlabel('Shift', fontsize=8)
    ax.set_ylabel('Defect %', fontsize=8)
    ax.set_title('Defect % by Shift', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    for i, v in enumerate(grouped['Defect %']):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontsize=7)
    st.pyplot(fig)

def show_plant_comparison(df):
    st.subheader("🏷️ Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(grouped['plant'], grouped['bottles_produced'])
    ax.set_xlabel('Plant', fontsize=8)
    ax.set_ylabel('Total Bottles Produced', fontsize=8)
    ax.set_title('Plant-wise Total Production', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    for i, v in enumerate(grouped['bottles_produced']):
        ax.text(i, v + 0.5, f"{int(v)}", ha='center', fontsize=7)
    st.pyplot(fig)
