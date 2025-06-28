# viz.py

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
    max_date = grouped.idxmax()
    min_date = grouped.idxmin()
    ax.scatter(max_date, grouped.max(), color='green', s=40, label='Max')
    ax.scatter(min_date, grouped.min(), color='red', s=40, label='Min')
    ax.set_xlabel('Date')
    ax.set_ylabel('Bottles Produced')
    ax.set_title('📈 Production Trend', fontsize=11)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(fontsize=7)
    st.pyplot(fig)
    st.caption(f"Highest: {grouped.max():,.0f} on {max_date.date()} | Lowest: {grouped.min():,.0f} on {min_date.date()}")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped['date'], grouped['defect_rate'], label='Defect Rate')
    if smoothing:
        smoothed = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        ax.plot(grouped['date'], smoothed, linestyle='--', label='7-day Avg')
    max_idx = grouped['defect_rate'].idxmax()
    min_idx = grouped['defect_rate'].idxmin()
    ax.scatter(grouped.loc[max_idx, 'date'], grouped['defect_rate'].max(), color='green', s=40, label='Max')
    ax.scatter(grouped.loc[min_idx, 'date'], grouped['defect_rate'].min(), color='red', s=40, label='Min')
    ax.set_xlabel('Date')
    ax.set_ylabel('Defect Rate (%)')
    ax.set_title('📉 Defect Rate Trend', fontsize=11)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(fontsize=7)
    st.pyplot(fig)
    st.caption(f"Highest: {grouped['defect_rate'].max():.2f}% | Lowest: {grouped['defect_rate'].min():.2f}%")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date')['downtime'].sum()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped.index, grouped.values, label='Downtime')
    if smoothing:
        smoothed = grouped.rolling(window=7, min_periods=1).mean()
        ax.plot(grouped.index, smoothed.values, linestyle='--', label='7-day Avg')
    max_date = grouped.idxmax()
    min_date = grouped.idxmin()
    ax.scatter(max_date, grouped.max(), color='green', s=40, label='Max')
    ax.scatter(min_date, grouped.min(), color='red', s=40, label='Min')
    ax.set_xlabel('Date')
    ax.set_ylabel('Downtime (mins)')
    ax.set_title('🕒 Downtime Trend', fontsize=11)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(fontsize=7)
    st.pyplot(fig)
    st.caption(f"Highest: {grouped.max():,.1f} mins on {max_date.date()} | Lowest: {grouped.min():,.1f} mins on {min_date.date()}")

def show_defect_vs_production_scatter(df):
    st.subheader("🔎 Defect Count vs. Bottles Produced")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(df['bottles_produced'], df['defect_count'], alpha=0.5)
    ax.set_xlabel('Bottles Produced')
    ax.set_ylabel('Defect Count')
    ax.set_title('Defect vs Production Scatter', fontsize=10)
    st.pyplot(fig)
    st.caption("Shows relation between total units and defect count across records.")

def show_shift_breakdown(df):
    st.subheader("📊 Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({
        'bottles_produced': 'sum',
        'defect_count': 'sum'
    }).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    max_shift = grouped.loc[grouped['Defect %'].idxmax(), 'shift']
    min_shift = grouped.loc[grouped['Defect %'].idxmin(), 'shift']

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(grouped['shift'].astype(str), grouped['Defect %'])
    ax.set_xlabel('Shift')
    ax.set_ylabel('Defect %')
    ax.set_title('Defect % by Shift', fontsize=10)
    for i, v in enumerate(grouped['Defect %']):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontsize=7)
    st.pyplot(fig)
    st.caption(f"Highest: Shift {max_shift} | Lowest: Shift {min_shift}")

def show_plant_comparison(df):
    st.subheader("🏷️ Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    max_plant = grouped.loc[grouped['bottles_produced'].idxmax(), 'plant']
    min_plant = grouped.loc[grouped['bottles_produced'].idxmin(), 'plant']

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(grouped['plant'], grouped['bottles_produced'])
    ax.set_xlabel('Plant')
    ax.set_ylabel('Total Bottles Produced')
    ax.set_title('Plant-wise Total Production', fontsize=10)
    for i, v in enumerate(grouped['bottles_produced']):
        ax.text(i, v + 0.5, f"{int(v)}", ha='center', fontsize=7)
    st.pyplot(fig)
    st.caption(f"Highest: {max_plant} | Lowest: {min_plant}")
