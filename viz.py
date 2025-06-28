import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore

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

def highlight_outliers(series, threshold=3):
    zs = zscore(series, nan_policy='omit')
    return np.abs(zs) > threshold

def show_production_trends(df, smoothing=True):
    grouped = df.groupby('date')['bottles_produced'].sum()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped.index, grouped.values, label='Raw')
    if smoothing:
        smoothed = grouped.rolling(window=7, min_periods=1).mean()
        ax.plot(grouped.index, smoothed.values, linestyle='--', label='7-day Avg')
    outliers = highlight_outliers(grouped)
    ax.scatter(grouped.index[outliers], grouped.values[outliers], color='red', s=40, label='Outlier', zorder=5)
    max_val, min_val = grouped.max(), grouped.min()
    max_date, min_date = grouped.idxmax(), grouped.idxmin()
    ax.scatter([max_date], [max_val], color='green', s=60, zorder=6)
    ax.scatter([min_date], [min_val], color='blue', s=60, zorder=6)
    ax.annotate(f"Peak\n{max_val:,.0f}", (max_date, max_val), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='green')
    ax.annotate(f"Low\n{min_val:,.0f}", (min_date, min_val), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=8, color='blue')
    ax.set_xlabel('Date', fontsize=8)
    ax.set_ylabel('Bottles Produced', fontsize=8)
    ax.set_title('📈 Production Trend', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    ax.legend(fontsize=7)
    st.pyplot(fig)
    st.caption(f"Peak: {max_val:,.0f} on {max_date.date()} | Low: {min_val:,.0f} on {min_date.date()}")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped['date'], grouped['defect_rate'], label='Defect Rate')
    if smoothing:
        smoothed = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        ax.plot(grouped['date'], smoothed, linestyle='--', label='7-day Avg')
    outliers = highlight_outliers(grouped['defect_rate'])
    ax.scatter(grouped['date'][outliers], grouped['defect_rate'][outliers], color='red', s=40, label='Outlier', zorder=5)
    max_val = grouped['defect_rate'].max()
    min_val = grouped['defect_rate'].min()
    max_date = grouped['date'][grouped['defect_rate'].idxmax()]
    min_date = grouped['date'][grouped['defect_rate'].idxmin()]
    ax.scatter([max_date], [max_val], color='green', s=60, zorder=6)
    ax.scatter([min_date], [min_val], color='blue', s=60, zorder=6)
    ax.annotate(f"Peak\n{max_val:.2f}%", (max_date, max_val), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='green')
    ax.annotate(f"Low\n{min_val:.2f}%", (min_date, min_val), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=8, color='blue')
    ax.set_xlabel('Date', fontsize=8)
    ax.set_ylabel('Defect Rate (%)', fontsize=8)
    ax.set_title('📉 Defect Rate Trend', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    ax.legend(fontsize=7)
    st.pyplot(fig)
    st.caption(f"Peak: {max_val:.2f}% on {max_date.date()} | Low: {min_val:.2f}% on {min_date.date()}")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date')['downtime'].sum()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(grouped.index, grouped.values, label='Downtime')
    if smoothing:
        smoothed = grouped.rolling(window=7, min_periods=1).mean()
        ax.plot(grouped.index, smoothed.values, linestyle='--', label='7-day Avg')
    outliers = highlight_outliers(grouped)
    ax.scatter(grouped.index[outliers], grouped.values[outliers], color='red', s=40, label='Outlier', zorder=5)
    max_val, min_val = grouped.max(), grouped.min()
    max_date, min_date = grouped.idxmax(), grouped.idxmin()
    ax.scatter([max_date], [max_val], color='green', s=60, zorder=6)
    ax.scatter([min_date], [min_val], color='blue', s=60, zorder=6)
    ax.annotate(f"Peak\n{max_val:,.1f}", (max_date, max_val), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='green')
    ax.annotate(f"Low\n{min_val:,.1f}", (min_date, min_val), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=8, color='blue')
    ax.set_xlabel('Date', fontsize=8)
    ax.set_ylabel('Downtime (mins)', fontsize=8)
    ax.set_title('🕒 Downtime Trend', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    ax.legend(fontsize=7)
    st.pyplot(fig)
    st.caption(f"Peak: {max_val:,.1f} mins on {max_date.date()} | Low: {min_val:,.1f} mins on {min_date.date()}")

def show_defect_vs_production_scatter(df):
    st.subheader("🔎 Defect Count vs. Bottles Produced")
    zs = zscore(df['defect_count'], nan_policy='omit')
    outliers = np.abs(zs) > 3
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.scatter(df['bottles_produced'][~outliers], df['defect_count'][~outliers], alpha=0.5, label='Normal')
    ax.scatter(df['bottles_produced'][outliers], df['defect_count'][outliers], color='red', alpha=0.7, label='Outlier')
    ax.set_xlabel('Bottles Produced', fontsize=8)
    ax.set_ylabel('Defect Count', fontsize=8)
    ax.set_title('Defect vs Production Scatter', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    ax.legend(fontsize=7)
    st.pyplot(fig)
    st.caption("Red points are statistical outliers (Z-score > 3).")

def show_shift_breakdown(df):
    st.subheader("📊 Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({
        'bottles_produced': 'sum',
        'defect_count': 'sum'
    }).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.bar(grouped['shift'].astype(str), grouped['Defect %'])
    ax.set_xlabel('Shift', fontsize=8)
    ax.set_ylabel('Defect %', fontsize=8)
    ax.set_title('Defect % by Shift', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    for i, v in enumerate(grouped['Defect %']):
        ax.text(i, v + 0.05, f"{v:.2f}%", ha='center', fontsize=7)
    st.pyplot(fig)
    st.caption(f"Highest: Shift {grouped.loc[grouped['Defect %'].idxmax(), 'shift']} | Lowest: Shift {grouped.loc[grouped['Defect %'].idxmin(), 'shift']}")

def show_plant_comparison(df):
    st.subheader("🏷️ Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.bar(grouped['plant'], grouped['bottles_produced'])
    ax.set_xlabel('Plant', fontsize=8)
    ax.set_ylabel('Total Bottles Produced', fontsize=8)
    ax.set_title('Plant-wise Total Production', fontsize=10)
    ax.tick_params(axis='both', labelsize=7)
    for i, v in enumerate(grouped['bottles_produced']):
        ax.text(i, v + 0.05 * grouped['bottles_produced'].max(), f"{int(v)}", ha='center', fontsize=7)
    st.pyplot(fig)
    st.caption(f"Highest: {grouped.loc[grouped['bottles_produced'].idxmax(), 'plant']} | Lowest: {grouped.loc[grouped['bottles_produced'].idxmin(), 'plant']}")

def show_kpi_insights(df):
    st.markdown("#### 📌 KPI Insights")
    prod = df.groupby('date')['bottles_produced'].sum()
    prod_trend = (prod[-7:].mean() - prod[-14:-7].mean()) / prod[-14:-7].mean() * 100 if len(prod) > 14 else 0
    st.write(f"**Production:** Last 7-day avg: {prod[-7:].mean():,.0f} | Change vs prev week: {prod_trend:+.2f}%")
    defect = df.groupby('date').apply(lambda x: x['defect_count'].sum() / x['bottles_produced'].sum() * 100)
    defect_trend = (defect[-7:].mean() - defect[-14:-7].mean()) / defect[-14:-7].mean() * 100 if len(defect) > 14 else 0
    st.write(f"**Defect Rate:** Last 7-day avg: {defect[-7:].mean():.2f}% | Change vs prev week: {defect_trend:+.2f}%")
    downtime = df.groupby('date')['downtime'].sum()
    downtime_trend = (downtime[-7:].mean() - downtime[-14:-7].mean()) / downtime[-14:-7].mean() * 100 if len(downtime) > 14 else 0
    st.write(f"**Downtime:** Last 7-day avg: {downtime[-7:].mean():.1f} mins | Change vs prev week: {downtime_trend:+.2f}%")

def show_top_days_table(df):
    st.markdown("#### 🏅 Top/Bottom 3 Days")
    prod = df.groupby('date')['bottles_produced'].sum()
    st.write("**Best Production Days:**")
    st.dataframe(prod.sort_values(ascending=False).head(3))
    st.write("**Worst Production Days:**")
    st.dataframe(prod.sort_values().head(3))
