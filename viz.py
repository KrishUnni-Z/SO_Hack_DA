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
    fig = px.line(grouped, x='date', y='bottles_produced', title='Production Trend')
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

    avg_prod = grouped['bottles_produced'].mean()
    max_val = grouped['bottles_produced'].max()
    min_val = grouped['bottles_produced'].min()
    max_date = grouped.loc[grouped['bottles_produced'].idxmax(), 'date']
    min_date = grouped.loc[grouped['bottles_produced'].idxmin(), 'date']
    st.write(f"On average, **{int(avg_prod):,}** bottles were produced daily. The highest was **{int(max_val):,}** on **{max_date.date()}**, and the lowest was **{int(min_val):,}** on **{min_date.date()}**.")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', title='Defect Rate Trend')
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

    avg_def = grouped['defect_rate'].mean()
    max_val = grouped['defect_rate'].max()
    min_val = grouped['defect_rate'].min()
    max_date = grouped.loc[grouped['defect_rate'].idxmax(), 'date']
    min_date = grouped.loc[grouped['defect_rate'].idxmin(), 'date']
    st.write(f"Average defect rate was **{avg_def:.2f}%**. The highest was **{max_val:.2f}%** on **{max_date.date()}**, and the lowest was **{min_val:.2f}%** on **{min_date.date()}**.")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='Downtime Trend')
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

    avg_down = grouped['downtime'].mean()
    max_val = grouped['downtime'].max()
    min_val = grouped['downtime'].min()
    max_date = grouped.loc[grouped['downtime'].idxmax(), 'date']
    min_date = grouped.loc[grouped['downtime'].idxmin(), 'date']
    st.write(f"Average downtime was **{avg_down:.1f} minutes**. The highest was **{max_val:.1f} minutes** on **{max_date.date()}**, and the lowest was **{min_val:.1f} minutes** on **{min_date.date()}**.")

def show_shift_breakdown(df):
    st.subheader("Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(grouped, x='shift', y='Defect %', title='Defect % by Shift')
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    highest_shift = grouped.loc[grouped['Defect %'].idxmax(), 'shift']
    lowest_shift = grouped.loc[grouped['Defect %'].idxmin(), 'shift']
    st.write(f"Shift **{highest_shift}** had the highest defect percentage, while Shift **{lowest_shift}** had the lowest defect percentage during this period.")

def show_plant_comparison(df):
    st.subheader("Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig = px.bar(grouped, x='plant', y='bottles_produced', title='Plant-wise Total Production')
    fig.update_traces(text=grouped['bottles_produced'].astype(int).astype(str), textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def show_kpi_insights(df):
    st.subheader("KPI Highlights")
    if df.empty:
        st.write("No data available for insights.")
        return

    col1, col2 = st.columns(2)
    with col1:
        prod_by_plant = df.groupby('plant')['bottles_produced'].sum().sort_values(ascending=False)
        st.markdown("**Total Production by Plant**")
        st.dataframe(prod_by_plant.to_frame(), use_container_width=True)
    with col2:
        defect_by_plant = df.groupby('plant')['defect_count'].sum().sort_values(ascending=False)
        st.markdown("**Total Defects by Plant**")
        st.dataframe(defect_by_plant.to_frame(), use_container_width=True)

    st.markdown("---")
    st.subheader("Daily Top Plants by Production & Defects")

    daily_prod = df.groupby(['date', 'plant'])['bottles_produced'].sum().reset_index()
    top_prod_per_day = daily_prod.loc[daily_prod.groupby('date')['bottles_produced'].idxmax()]
    st.write("Each day, the plant with the highest production:")
    st.dataframe(top_prod_per_day[['date', 'plant', 'bottles_produced']], use_container_width=True)

    daily_defects = df.groupby(['date', 'plant'])['defect_count'].sum().reset_index()
    top_defects_per_day = daily_defects.loc[daily_defects.groupby('date')['defect_count'].idxmax()]
    st.write("Each day, the plant with the highest defect count:")
    st.dataframe(top_defects_per_day[['date', 'plant', 'defect_count']], use_container_width=True)

    st.markdown("---")
    st.subheader("Plant-wise Defect Rate Distribution")
    defect_rates = df.groupby('plant').apply(lambda x: x['defect_count'].sum() / x['bottles_produced'].sum() * 100).reset_index(name='Defect Rate %')
    fig = px.bar(defect_rates, x='plant', y='Defect Rate %', title='Defect Rate % by Plant')
    st.plotly_chart(fig, use_container_width=True)

    st.write("This chart shows which plants had higher or lower average defect rates over the selected period.")
