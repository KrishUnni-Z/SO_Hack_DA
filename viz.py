import os
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from scipy.stats import zscore

def highlight_outliers(series, threshold=3):
    zs = zscore(series, nan_policy='omit')
    return np.abs(zs) > threshold

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
    grouped = df.groupby('date', as_index=False)['bottles_produced'].sum()
    fig = px.line(grouped, x='date', y='bottles_produced', title='📈 Production Trend', labels={'bottles_produced': 'Bottles Produced'})
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', title='📉 Defect Rate Trend', labels={'defect_rate': 'Defect Rate (%)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='🕒 Downtime Trend', labels={'downtime': 'Downtime (mins)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

def show_shift_breakdown(df):
    st.subheader("📊 Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({
        'bottles_produced': 'sum',
        'defect_count': 'sum'
    }).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(grouped, x='shift', y='Defect %', title='Defect % by Shift')
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def show_plant_comparison(df):
    st.subheader("🏷️ Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig = px.bar(grouped, x='plant', y='bottles_produced', title='Plant-wise Total Production')
    fig.update_traces(text=grouped['bottles_produced'].astype(int).astype(str), textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def show_kpi_insights(df):
    st.subheader("📌 KPI Highlights")
    if df.empty:
        st.write("No data available for insights.")
        return
    col1, col2 = st.columns(2)
    with col1:
        prod_by_plant = df.groupby('plant')['bottles_produced'].sum().sort_values(ascending=False)
        st.markdown("**🏭 Production by Plant**")
        st.dataframe(prod_by_plant.to_frame(), use_container_width=True)
    with col2:
        defect_by_plant = df.groupby('plant')['defect_count'].sum().sort_values(ascending=False)
        st.markdown("**❌ Defects by Plant**")
        st.dataframe(defect_by_plant.to_frame(), use_container_width=True)
    st.markdown("---")
    st.markdown("#### 📅 Daily Production Summary")
    daily_summary = df.groupby('date').agg({
        'bottles_produced': 'sum',
        'defect_count': 'sum',
        'downtime': 'sum'
    }).reset_index()
    fig = px.bar(daily_summary, x='date', y='bottles_produced', title="Daily Production")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.markdown("#### 🏆 Top & Bottom Days by Production")
    top_days = daily_summary.nlargest(3, 'bottles_produced')[['date', 'bottles_produced']]
    bottom_days = daily_summary.nsmallest(3, 'bottles_produced')[['date', 'bottles_produced']]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Best Days**")
        st.table(top_days)
    with col2:
        st.markdown("**Worst Days**")
        st.table(bottom_days)

def show_plant_defect_heatmap(df):
    st.subheader("🌡️ Plant vs. Shift Defect Heatmap")
    pivot = df.pivot_table(index='plant', columns='shift', values='defect_count', aggfunc='sum').fillna(0)
    fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale='Reds', title="Total Defects by Plant & Shift")
    st.plotly_chart(fig, use_container_width=True)
