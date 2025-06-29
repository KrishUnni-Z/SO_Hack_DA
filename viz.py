import os
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np

# Utility: Always use this to map numeric shift codes to 'A', 'B', 'C'
def map_shifts(df):
    shift_map = {'1': 'A', '2': 'B', '3': 'C', 1: 'A', 2: 'B', 3: 'C'}
    if 'shift' in df.columns:
        df['shift'] = df['shift'].astype(str).map(shift_map).fillna(df['shift'])
    return df

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
        if 'shift' in combined.columns:
            combined = map_shifts(combined)
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

# --- Main Plots ---

def show_production_trends(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['bottles_produced'].sum()
    fig = px.line(grouped, x='date', y='bottles_produced', title='Production Trend', labels={'bottles_produced': 'Bottles Produced'})
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg_val = grouped['bottles_produced'].mean()
    max_val = grouped['bottles_produced'].max()
    min_val = grouped['bottles_produced'].min()
    max_date = grouped.loc[grouped['bottles_produced'].idxmax(), 'date']
    min_date = grouped.loc[grouped['bottles_produced'].idxmin(), 'date']
    st.info(f"Average Daily Production: {avg_val:,.0f} bottles | Highest: {max_val:,.0f} on {max_date.date()} | Lowest: {min_val:,.0f} on {min_date.date()}")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', title='Defect Rate Trend', labels={'defect_rate': 'Defect Rate (%)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg_val = grouped['defect_rate'].mean()
    max_val = grouped['defect_rate'].max()
    min_val = grouped['defect_rate'].min()
    max_date = grouped.loc[grouped['defect_rate'].idxmax(), 'date']
    min_date = grouped.loc[grouped['defect_rate'].idxmin(), 'date']
    st.info(f"Average Defect Rate: {avg_val:.2f}% | Highest: {max_val:.2f}% on {max_date.date()} | Lowest: {min_val:.2f}% on {min_date.date()}")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='Downtime Trend', labels={'downtime': 'Downtime (mins)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg_val = grouped['downtime'].mean()
    max_val = grouped['downtime'].max()
    min_val = grouped['downtime'].min()
    max_date = grouped.loc[grouped['downtime'].idxmax(), 'date']
    min_date = grouped.loc[grouped['downtime'].idxmin(), 'date']
    st.info(f"Average Downtime: {avg_val:.1f} mins | Highest: {max_val:.1f} mins on {max_date.date()} | Lowest: {min_val:.1f} mins on {min_date.date()}")

def show_shift_breakdown(df):
    df = map_shifts(df)
    st.subheader("Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(
        grouped, x='shift', y='Defect %', 
        title='Defect % by Shift',
        labels={'shift': 'Shift', 'Defect %': 'Defect Percentage (%)'}
    )
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    max_shift = grouped.loc[grouped['Defect %'].idxmax(), 'shift']
    min_shift = grouped.loc[grouped['Defect %'].idxmin(), 'shift']
    shift_counts = df['shift'].value_counts()
    rare_shifts = shift_counts[shift_counts < shift_counts.max() * 0.6]
    msg = f"Shift {max_shift} has the highest defect percentage; Shift {min_shift} has the lowest."
    if not rare_shifts.empty:
        msg += f" Note: Shifts {', '.join(rare_shifts.index)} have much fewer records and their rates may not be reliable."
    st.info(msg)

def show_plant_comparison(df):
    st.subheader("Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index().sort_values(by='bottles_produced', ascending=False)
    fig = px.bar(
        grouped, x='plant', y='bottles_produced',
        title='Plant-wise Total Production',
        labels={'plant': 'Plant', 'bottles_produced': 'Total Bottles Produced'}
    )
    fig.update_traces(text=grouped['bottles_produced'].astype(int).astype(str), textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    max_plant = grouped.iloc[0]['plant']
    min_plant = grouped.iloc[-1]['plant']
    st.info(f"{max_plant} produced the most bottles overall, while {min_plant} produced the least.")

def show_downtime_contribution_by_shift(df):
    df = map_shifts(df)
    st.subheader("Downtime Contribution by Shift")
    grouped = df.groupby('shift')['downtime'].sum().reset_index()
    fig = px.pie(grouped, names='shift', values='downtime', title='Share of Total Downtime by Shift')
    st.plotly_chart(fig, use_container_width=True)
    top_shift = grouped.loc[grouped['downtime'].idxmax(), 'shift']
    st.info(f"Shift {top_shift} contributed the most to total downtime in minutes.")

def show_heatmap_defect_rates(df):
    df = map_shifts(df)
    st.subheader("Defect Rates by Plant and Shift")
    pivot = df.pivot_table(index='plant', columns='shift', values='defect_count', aggfunc='sum').fillna(0)
    fig = px.imshow(
        pivot, text_auto=True, aspect="auto", color_continuous_scale='Reds',
        labels={'color': 'Defects'}, title="Total Defects by Plant & Shift"
    )
    st.plotly_chart(fig, use_container_width=True)
    plant_max = pivot.sum(axis=1).idxmax()
    shift_max = pivot.sum().idxmax()
    st.info(f"Most total defects come from plant {plant_max} and shift {shift_max}.")

def show_dayofweek_production(df):
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    prod = df.groupby('day_of_week')['bottles_produced'].mean().reindex(dow_order)
    fig1 = px.bar(
        x=prod.index, y=prod.values, 
        labels={'x': 'Day of Week', 'y': 'Avg Bottles Produced'},
        title="Avg Production by Day"
    )
    st.plotly_chart(fig1, use_container_width=True)
    max_prod_day = prod.idxmax()
    min_prod_day = prod.idxmin()
    st.info(f"Production is highest on {max_prod_day} and lowest on {min_prod_day}.")

def show_dayofweek_defects(df):
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    defects = df.groupby('day_of_week')['defect_count'].mean().reindex(dow_order)
    fig2 = px.bar(
        x=defects.index, y=defects.values, 
        labels={'x': 'Day of Week', 'y': 'Avg Defect Count'},
        title="Avg Defects by Day"
    )
    st.plotly_chart(fig2, use_container_width=True)
    max_def_day = defects.idxmax()
    min_def_day = defects.idxmin()
    st.info(f"Defects are highest on {max_def_day} and lowest on {min_def_day}.")

def show_monthly_summary_table(df):
    st.subheader("Monthly Summary Table")
    df['month'] = df['date'].dt.strftime('%Y-%m')
    # Days in each month
    days_per_month = df.groupby('month')['date'].nunique().reset_index(name='Days in Month')
    # Highest producing plant per month
    monthly_prod = df.groupby(['month', 'plant'])['bottles_produced'].sum().reset_index()
    idx = monthly_prod.groupby('month')['bottles_produced'].idxmax()
    top_plant_month = monthly_prod.loc[idx][['month', 'plant']].rename(columns={'plant': 'Top Plant'})
    # Most defects in plant per month
    monthly_def = df.groupby(['month', 'plant'])['defect_count'].sum().reset_index()
    idx2 = monthly_def.groupby('month')['defect_count'].idxmax()
    most_defect_plant = monthly_def.loc[idx2][['month', 'plant']].rename(columns={'plant': 'Most Defects Plant'})
    # Highest/lowest downtime plant per month
    monthly_dt = df.groupby(['month', 'plant'])['downtime'].sum().reset_index()
    idx3 = monthly_dt.groupby('month')['downtime'].idxmax()
    idx4 = monthly_dt.groupby('month')['downtime'].idxmin()
    hi_dt_plant = monthly_dt.loc[idx3][['month', 'plant']].rename(columns={'plant': 'High Downtime Plant'})
    lo_dt_plant = monthly_dt.loc[idx4][['month', 'plant']].rename(columns={'plant': 'Low Downtime Plant'})
    # Aggregates
    summary = df.groupby('month').agg({
        'bottles_produced': 'mean',
        'defect_count': 'mean',
        'downtime': 'mean'
    }).rename(columns={
        'bottles_produced': 'Avg Production',
        'defect_count': 'Avg Defects',
        'downtime': 'Avg Downtime (mins)'
    }).reset_index()
    # Merge
    summary = summary.merge(days_per_month, on='month')
    summary = summary.merge(top_plant_month, on='month')
    summary = summary.merge(most_defect_plant, on='month')
    summary = summary.merge(hi_dt_plant, on='month')
    summary = summary.merge(lo_dt_plant, on='month')
    st.dataframe(summary, use_container_width=True)
    st.info(
        f"This table summarises monthly averages, number of operating days, and top/bottom performing plants for each metric."
    )

def show_kpi_insights(df):
    st.subheader("KPI Highlights")
    if df.empty:
        st.write("No data available for insights.")
        return
    col1, col2 = st.columns(2)
    with col1:
        prod_by_plant = df.groupby('plant')['bottles_produced'].sum().sort_values(ascending=False)
        st.markdown("**Production by Plant (Sorted):**")
        st.dataframe(prod_by_plant.to_frame(), use_container_width=True)
    with col2:
        defect_by_plant = df.groupby('plant')['defect_count'].sum().sort_values(ascending=False)
        st.markdown("**Defects by Plant (Sorted):**")
        st.dataframe(defect_by_plant.to_frame(), use_container_width=True)

    st.markdown("---")
    st.subheader("Daily Plant Leaders")
    daily_prod = df.groupby(['date', 'plant'])['bottles_produced'].sum().reset_index()
    top_prod_per_day = daily_prod.loc[daily_prod.groupby('date')['bottles_produced'].idxmax()]
    st.markdown("**Table: Days where each plant led daily production (sorted):**")
    st.dataframe(top_prod_per_day[['date', 'plant', 'bottles_produced']].sort_values('bottles_produced', ascending=False), use_container_width=True)

    daily_defects = df.groupby(['date', 'plant'])['defect_count'].sum().reset_index()
    top_defects_per_day = daily_defects.loc[daily_defects.groupby('date')['defect_count'].idxmax()]
    st.markdown("**Table: Days where each plant had the highest defects (sorted):**")
    st.dataframe(top_defects_per_day[['date', 'plant', 'defect_count']].sort_values('defect_count', ascending=False), use_container_width=True)

    st.markdown("---")
    show_monthly_summary_table(df)
    st.markdown("---")
    show_heatmap_defect_rates(df)
    st.markdown("---")
    show_downtime_contribution_by_shift(df)
    st.markdown("---")
    show_downtime_defect_correlation(df)
    st.markdown("---")
    st.subheader("Weekday Trends")
    show_dayofweek_production(df)
    show_dayofweek_defects(df)

def show_downtime_defect_correlation(df):
    st.subheader("Downtime vs. Defects Correlation")
    corr_df = df.groupby('date').agg({'downtime': 'sum', 'defect_count': 'sum'}).reset_index()
    fig = px.scatter(
        corr_df, x='downtime', y='defect_count',
        labels={'downtime': 'Downtime (mins)', 'defect_count': 'Defects'},
        title='Daily Downtime vs. Defects',
        trendline="ols"
    )
    st.plotly_chart(fig, use_container_width=True)
    corr_val = corr_df['downtime'].corr(corr_df['defect_count'])
    abs_corr = abs(corr_val)
    if abs_corr > 0.7:
        relation = "strong"
    elif abs_corr > 0.3:
        relation = "moderate"
    else:
        relation = "weak or no"
    st.info(
        f"Pearson correlation (absolute value) between downtime and defects: {abs_corr:.2f}. "
        f"This suggests a {relation} linear relationship between downtime and defects."
    )
