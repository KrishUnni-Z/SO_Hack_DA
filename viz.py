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
    fig = px.line(grouped, x='date', y='bottles_produced', title='Production Trend', labels={'bottles_produced': 'Bottles Produced'}, height=400)
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg_prod = grouped['bottles_produced'].mean()
    max_prod = grouped['bottles_produced'].max()
    min_prod = grouped['bottles_produced'].min()
    max_day = grouped.loc[grouped['bottles_produced'].idxmax(), 'date'].date()
    min_day = grouped.loc[grouped['bottles_produced'].idxmin(), 'date'].date()
    st.markdown(f"**Across the selected period, the average daily production was {avg_prod:,.0f} bottles. The highest daily output was {max_prod:,.0f} on {max_day}, while the lowest was {min_prod:,.0f} on {min_day}.**")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', title='Defect Rate Trend', labels={'defect_rate': 'Defect Rate (%)'}, height=400)
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg_def = grouped['defect_rate'].mean()
    max_def = grouped['defect_rate'].max()
    min_def = grouped['defect_rate'].min()
    max_day = grouped.loc[grouped['defect_rate'].idxmax(), 'date'].date()
    min_day = grouped.loc[grouped['defect_rate'].idxmin(), 'date'].date()
    st.markdown(f"**The average defect rate was {avg_def:.2f}%. The highest defect rate was {max_def:.2f}% on {max_day}, while the lowest was {min_def:.2f}% on {min_day}.**")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='Downtime Trend', labels={'downtime': 'Downtime (mins)'}, height=400)
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg_down = grouped['downtime'].mean()
    max_down = grouped['downtime'].max()
    min_down = grouped['downtime'].min()
    max_day = grouped.loc[grouped['downtime'].idxmax(), 'date'].date()
    min_day = grouped.loc[grouped['downtime'].idxmin(), 'date'].date()
    st.markdown(f"**Average downtime was {avg_down:.1f} minutes per day. The maximum was {max_down:.1f} mins on {max_day}, and the minimum was {min_down:.1f} mins on {min_day}.**")

def show_shift_breakdown(df):
    st.subheader("Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(grouped, x='shift', y='Defect %', title='Defect % by Shift', height=400)
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    max_shift = grouped.loc[grouped['Defect %'].idxmax()]
    min_shift = grouped.loc[grouped['Defect %'].idxmin()]
    st.markdown(f"**Shift {max_shift['shift']} had the highest defect percentage at {max_shift['Defect %']:.2f}%. Shift {min_shift['shift']} had the lowest at {min_shift['Defect %']:.2f}%.**")

def show_plant_comparison(df):
    st.subheader("Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig = px.bar(grouped, x='plant', y='bottles_produced', title='Plant-wise Total Production', height=350)
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
        st.markdown("**Production by Plant**")
        st.dataframe(prod_by_plant.to_frame(), use_container_width=True)
    with col2:
        defect_by_plant = df.groupby('plant')['defect_count'].sum().sort_values(ascending=False)
        st.markdown("**Defects by Plant**")
        st.dataframe(defect_by_plant.to_frame(), use_container_width=True)

    st.markdown("---")
    st.subheader("Daily Plant-wise Production & Defects Comparison")

    # Daily Production by Plant
    daily_prod = df.groupby(['date', 'plant'])['bottles_produced'].sum().reset_index()
    # For each date, find the plant with max production
    top_prod_per_day = daily_prod.loc[daily_prod.groupby('date')['bottles_produced'].idxmax()]
    fig_prod = px.bar(top_prod_per_day, x='date', y='bottles_produced', color='plant', title='Plant with Highest Daily Production', height=350)
    st.plotly_chart(fig_prod, use_container_width=True)
    st.markdown("**Above: For each day, this shows only the plant that had the highest production.**")
    st.dataframe(top_prod_per_day[['date', 'plant', 'bottles_produced']])

    st.markdown("---")
    # Daily Defects by Plant
    daily_defects = df.groupby(['date', 'plant'])['defect_count'].sum().reset_index()
    top_defects_per_day = daily_defects.loc[daily_defects.groupby('date')['defect_count'].idxmax()]
    fig_defect = px.bar(top_defects_per_day, x='date', y='defect_count', color='plant', title='Plant with Highest Daily Defects', height=350)
    st.plotly_chart(fig_defect, use_container_width=True)
    st.markdown("**Above: For each day, this shows only the plant that had the highest number of defects.**")
    st.dataframe(top_defects_per_day[['date', 'plant', 'defect_count']])

    st.markdown("---")
    # Additional insights, correlation, or other plots can be added here as needed

# --- Additional business-value plots for Insights tab ---

def show_production_vs_defect_rate(df):
    st.subheader("Production vs Defect Rate Over Time")
    grouped = df.groupby('date').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    melted = pd.melt(grouped, id_vars=['date'], value_vars=['bottles_produced', 'defect_rate'])
    fig = px.line(melted, x='date', y='value', color='variable', title="Production & Defect Rate Over Time", height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"**This plot helps compare total daily production (left axis) to defect rate (right axis, %). Look for periods where higher output may coincide with higher/lower defect rates.**"
    )

def show_downtime_contribution_by_shift(df):
    st.subheader("Downtime Contribution by Shift")
    grouped = df.groupby('shift')['downtime'].sum().reset_index()
    fig = px.pie(grouped, values='downtime', names='shift', title="Share of Total Downtime by Shift", height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"**This chart shows the share of total downtime attributable to each shift, highlighting potential bottlenecks.**"
    )

def show_monthly_summary_table(df):
    st.subheader("Monthly Summary Table")
    df['month'] = df['date'].dt.to_period('M')
    grouped = df.groupby('month').agg(
        avg_production=('bottles_produced', 'mean'),
        avg_defects=('defect_count', 'mean'),
        avg_downtime=('downtime', 'mean')
    ).reset_index()
    grouped['pct_change_prod'] = grouped['avg_production'].pct_change().fillna(0) * 100
    grouped['pct_change_def'] = grouped['avg_defects'].pct_change().fillna(0) * 100
    grouped['pct_change_down'] = grouped['avg_downtime'].pct_change().fillna(0) * 100
    grouped = grouped.astype({'avg_production': int, 'avg_defects': int, 'avg_downtime': int})
    st.dataframe(grouped.rename(columns={
        'month': 'Month',
        'avg_production': 'Avg Production',
        'avg_defects': 'Avg Defects',
        'avg_downtime': 'Avg Downtime',
        'pct_change_prod': '% Change Prod.',
        'pct_change_def': '% Change Defects',
        'pct_change_down': '% Change Downtime'
    }), use_container_width=True)
    st.markdown(
        f"**Review monthly changes in key KPIs and quickly spot months with positive/negative performance trends.**"
    )

def show_heatmap_defect_rates(df):
    st.subheader("Heatmap of Defect Rates by Plant & Shift")
    pivot = df.pivot_table(index='plant', columns='shift', values='defect_count', aggfunc='sum').fillna(0)
    fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale='Reds', title="Total Defects by Plant & Shift", height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"**This heatmap helps spot which plants or shifts have consistently higher defect counts, so managers can act quickly.**"
    )

def show_high_vs_low_performance_days(df):
    st.subheader("High vs Low Performance Days")
    grouped = df.groupby('date').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.scatter(grouped, x='bottles_produced', y='defect_rate', title="Daily Output vs Defect Rate", labels={'bottles_produced': 'Daily Production', 'defect_rate': 'Defect Rate (%)'}, height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"**Each point is a day. Points at top left are low output/high defect days, while bottom right are high output/low defect days. Outliers indicate days needing review.**"
    )

def show_downtime_vs_defects_correlation(df):
    st.subheader("Downtime vs. Defects Correlation")
    grouped = df.groupby('date').agg({'downtime': 'sum', 'defect_count': 'sum'}).reset_index()
    fig = px.scatter(grouped, x='downtime', y='defect_count', title="Daily Downtime vs Defect Count", height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"**See if higher downtime is associated with more defects, which may suggest operational stress points.**"
    )
