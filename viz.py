import os
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from scipy.stats import zscore
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
    fig = px.line(grouped, x='date', y='bottles_produced', title='Production Trend by Date', labels={'bottles_produced': 'Bottles Produced (units)', 'date': 'Date'})
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    # Highlight high, low, avg
    high = grouped['bottles_produced'].max()
    low = grouped['bottles_produced'].min()
    avg = grouped['bottles_produced'].mean()
    high_date = grouped.loc[grouped['bottles_produced'].idxmax(), 'date']
    low_date = grouped.loc[grouped['bottles_produced'].idxmin(), 'date']
    fig.add_scatter(x=[high_date], y=[high], mode='markers+text', text=['High'], marker=dict(color='green', size=12), name='Highest')
    fig.add_scatter(x=[low_date], y=[low], mode='markers+text', text=['Low'], marker=dict(color='red', size=12), name='Lowest')
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Across the selected period, the average daily production was **{avg:,.0f} bottles**. The highest daily output was **{high:,.0f}** on **{high_date.date()}**, while the lowest was **{low:,.0f}** on **{low_date.date()}**.")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', title='Defect Rate Trend by Date', labels={'defect_rate': 'Defect Rate (%)', 'date': 'Date'})
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    high = grouped['defect_rate'].max()
    low = grouped['defect_rate'].min()
    avg = grouped['defect_rate'].mean()
    high_date = grouped.loc[grouped['defect_rate'].idxmax(), 'date']
    low_date = grouped.loc[grouped['defect_rate'].idxmin(), 'date']
    fig.add_scatter(x=[high_date], y=[high], mode='markers+text', text=['High'], marker=dict(color='green', size=12), name='Highest')
    fig.add_scatter(x=[low_date], y=[low], mode='markers+text', text=['Low'], marker=dict(color='red', size=12), name='Lowest')
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Across the selected period, the average defect rate was **{avg:.2f}%**. The highest rate was **{high:.2f}%** on **{high_date.date()}**, while the lowest was **{low:.2f}%** on **{low_date.date()}**.")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='Downtime Trend by Date', labels={'downtime': 'Downtime (mins)', 'date': 'Date'})
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    high = grouped['downtime'].max()
    low = grouped['downtime'].min()
    avg = grouped['downtime'].mean()
    high_date = grouped.loc[grouped['downtime'].idxmax(), 'date']
    low_date = grouped.loc[grouped['downtime'].idxmin(), 'date']
    fig.add_scatter(x=[high_date], y=[high], mode='markers+text', text=['High'], marker=dict(color='green', size=12), name='Highest')
    fig.add_scatter(x=[low_date], y=[low], mode='markers+text', text=['Low'], marker=dict(color='red', size=12), name='Lowest')
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Across the selected period, the average downtime was **{avg:.1f} minutes** per day. The highest was **{high:.1f} mins** on **{high_date.date()}**, and the lowest was **{low:.1f} mins** on **{low_date.date()}**.")

def show_shift_breakdown(df):
    st.subheader("Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(grouped, x='shift', y='Defect %', title='Defect % by Shift', labels={'Defect %': 'Defect Rate (%)', 'shift': 'Shift'})
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    max_shift = grouped.loc[grouped['Defect %'].idxmax()]
    min_shift = grouped.loc[grouped['Defect %'].idxmin()]
    st.info(f"Shift **{max_shift['shift']}** had the highest defect rate ({max_shift['Defect %']:.2f}%), while shift **{min_shift['shift']}** had the lowest ({min_shift['Defect %']:.2f}%).")

def show_plant_comparison(df):
    st.subheader("Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    grouped = grouped.sort_values(by='bottles_produced', ascending=False)
    fig = px.bar(grouped, x='plant', y='bottles_produced', title='Plant-wise Total Production', labels={'plant': 'Plant', 'bottles_produced': 'Total Bottles Produced (units)'})
    fig.update_traces(text=grouped['bottles_produced'].astype(int).astype(str), textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Plant **{grouped.iloc[0]['plant']}** produced the most bottles (**{int(grouped.iloc[0]['bottles_produced']):,} units**).")

def show_kpi_insights(df):
    st.header("Key Production & Defect Insights")
    if df.empty:
        st.write("No data available for insights.")
        return
    # Production by Plant
    st.subheader("Total Production by Plant")
    prod_by_plant = df.groupby('plant')['bottles_produced'].sum().sort_values(ascending=False)
    st.dataframe(prod_by_plant.to_frame().reset_index(), use_container_width=True)
    # Defects by Plant
    st.subheader("Total Defects by Plant")
    defect_by_plant = df.groupby('plant')['defect_count'].sum().sort_values(ascending=False)
    st.dataframe(defect_by_plant.to_frame().reset_index(), use_container_width=True)

    # Daily highest production plant per day
    st.subheader("Plant with Highest Daily Production (by Date)")
    daily_prod = df.groupby(['date', 'plant'])['bottles_produced'].sum().reset_index()
    top_prod_per_day = daily_prod.loc[daily_prod.groupby('date')['bottles_produced'].idxmax()]
    top_prod_per_day = top_prod_per_day.sort_values("bottles_produced", ascending=False)
    st.dataframe(top_prod_per_day[['date', 'plant', 'bottles_produced']], use_container_width=True)

    # Daily highest defects plant per day
    st.subheader("Plant with Highest Daily Defects (by Date)")
    daily_defects = df.groupby(['date', 'plant'])['defect_count'].sum().reset_index()
    top_defects_per_day = daily_defects.loc[daily_defects.groupby('date')['defect_count'].idxmax()]
    top_defects_per_day = top_defects_per_day.sort_values("defect_count", ascending=False)
    st.dataframe(top_defects_per_day[['date', 'plant', 'defect_count']], use_container_width=True)

def show_production_vs_defect_rate(df):
    # For combined trends
    grouped = df.groupby('date').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    long_df = grouped.melt(id_vars='date', value_vars=['bottles_produced', 'defect_rate'], var_name='variable', value_name='value')
    fig = px.line(long_df, x='date', y='value', color='variable', title='Production & Defect Rate Over Time', labels={'date': 'Date', 'value': 'Value'})
    st.plotly_chart(fig, use_container_width=True)
    st.info("Production and defect rate are plotted together for direct trend comparison.")

def show_monthly_summary(df):
    df['month'] = df['date'].dt.to_period('M')
    summary = df.groupby('month').agg({
        'bottles_produced': 'mean',
        'defect_count': 'mean',
        'downtime': 'mean',
        'date': 'count'
    }).rename(columns={'bottles_produced': 'Avg Production', 'defect_count': 'Avg Defects', 'downtime': 'Avg Downtime', 'date': 'Days'})
    summary['% Change Prod.'] = summary['Avg Production'].pct_change().fillna(0) * 100
    summary['% Change Defects'] = summary['Avg Defects'].pct_change().fillna(0) * 100
    summary['% Change Downtime'] = summary['Avg Downtime'].pct_change().fillna(0) * 100
    summary = summary.reset_index()
    st.subheader("Monthly Summary Table")
    st.dataframe(summary, use_container_width=True)
    st.info("Monthly averages for production, defects, and downtime with % change and number of days in each month.")

def show_defect_heatmap(df):
    st.subheader("Defect Rate Heatmap (Plant vs Shift)")
    pivot = df.groupby(['plant', 'shift']).agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    pivot['defect_rate'] = (pivot['defect_count'] / pivot['bottles_produced']) * 100
    heatmap_df = pivot.pivot(index='plant', columns='shift', values='defect_rate').fillna(0)
    fig = px.imshow(heatmap_df, text_auto=True, aspect="auto", color_continuous_scale='Reds', title="Defect Rate (%) by Plant & Shift")
    st.plotly_chart(fig, use_container_width=True)
    st.info("This heatmap shows which plant/shift combinations are underperforming based on defect rate.")

def show_production_vs_defects_scatter(df):
    st.subheader("Production vs Defect Rate Scatter")
    daily = df.groupby('date').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    daily['defect_rate'] = (daily['defect_count'] / daily['bottles_produced']) * 100
    fig = px.scatter(daily, x='bottles_produced', y='defect_rate', trendline='ols', labels={'bottles_produced': 'Production (units)', 'defect_rate': 'Defect Rate (%)'})
    st.plotly_chart(fig, use_container_width=True)
    st.info("Each point represents a day; the trend line shows the relationship between output and defect rate.")

def show_downtime_vs_defects_scatter(df):
    st.subheader("Downtime vs Defect Count Scatter")
    daily = df.groupby('date').agg({'downtime': 'sum', 'defect_count': 'sum'}).reset_index()
    fig = px.scatter(daily, x='downtime', y='defect_count', trendline='ols', labels={'downtime': 'Downtime (mins)', 'defect_count': 'Defect Count'})
    st.plotly_chart(fig, use_container_width=True)
    st.info("Explores the relationship between downtime and defects. Points trending upward together may signal operational stress.")

