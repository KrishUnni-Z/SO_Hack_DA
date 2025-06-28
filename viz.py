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
    st.write(f"Average daily production was **{int(avg_prod):,}** bottles. The highest was **{int(max_val):,}** on **{max_date.date()}**, while the lowest was **{int(min_val):,}** on **{min_date.date()}**.")

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
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(grouped, x='shift', y='Defect %', title='Defect % by Shift')
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    highest_shift = grouped.loc[grouped['Defect %'].idxmax(), 'shift']
    lowest_shift = grouped.loc[grouped['Defect %'].idxmin(), 'shift']
    st.write(f"Shift **{highest_shift}** had the highest defect rate, while Shift **{lowest_shift}** had the lowest.")

def show_plant_comparison(df):
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig = px.bar(grouped, x='plant', y='bottles_produced', title='Plant-wise Total Production')
    fig.update_traces(text=grouped['bottles_produced'].astype(int).astype(str), textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def show_kpi_insights(df):
    st.subheader("Production vs Defect Rate Over Time")
    daily = df.groupby('date').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    daily['defect_rate'] = (daily['defect_count'] / daily['bottles_produced']) * 100
    fig = px.line(daily, x='date', y=['bottles_produced', 'defect_rate'], title='Production & Defect Rate Over Time')
    st.plotly_chart(fig, use_container_width=True)
    st.write("This shows how production volume and defect rate evolved over time, helping identify trade-offs or spikes in quality issues.")

    st.subheader("Downtime Contribution by Shift")
    shift_downtime = df.groupby('shift')['downtime'].sum().reset_index()
    fig = px.pie(shift_downtime, names='shift', values='downtime', title='Downtime by Shift')
    st.plotly_chart(fig, use_container_width=True)
    st.write("This chart highlights which shift contributes most to overall downtime, useful for targeting process improvements.")

    st.subheader("Monthly Summary Table")
    monthly = df.groupby(df['date'].dt.to_period('M')).agg({
        'bottles_produced': 'mean',
        'defect_count': 'mean',
        'downtime': 'mean'
    }).reset_index()
    monthly['date'] = monthly['date'].dt.strftime('%Y-%m')
    st.dataframe(monthly)
    st.write("Monthly averages of key metrics provide a high-level overview of trends and operational stability.")

    st.subheader("Heatmap of Defect Rates by Plant & Shift")
    pivot = df.pivot_table(index='plant', columns='shift', values='defect_count', aggfunc='sum').fillna(0)
    fig = px.imshow(pivot, text_auto=True, aspect='auto', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)
    st.write("This heatmap helps managers quickly spot plants and shifts with higher defect volumes.")

    st.subheader("High vs Low Performance Days")
    fig = px.scatter(daily, x='bottles_produced', y='defect_rate', title='Daily Production vs Defect Rate')
    st.plotly_chart(fig, use_container_width=True)
    st.write("Days with high production and low defect rates show strong performance. Clusters with high defect rates need investigation.")

    st.subheader("Downtime vs Defects Correlation")
    daily_downtime = df.groupby('date')['downtime'].sum()
    fig = px.scatter(x=daily_downtime, y=daily['defect_count'], labels={'x': 'Downtime', 'y': 'Defects'}, title='Downtime vs Defects')
    st.plotly_chart(fig, use_container_width=True)
    st.write("This scatter shows if high downtime correlates with high defects, helping diagnose operational stress points.")
