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
    fig = px.line(grouped, x='date', y='bottles_produced', title='Production Trend', labels={'bottles_produced': 'Bottles Produced'})
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    # Highlight high/low points
    max_val = grouped['bottles_produced'].max()
    min_val = grouped['bottles_produced'].min()
    max_date = grouped.loc[grouped['bottles_produced'].idxmax(), 'date']
    min_date = grouped.loc[grouped['bottles_produced'].idxmin(), 'date']
    fig.add_scatter(x=[max_date], y=[max_val], mode='markers', marker=dict(color='green', size=10), name='Highest')
    fig.add_scatter(x=[min_date], y=[min_val], mode='markers', marker=dict(color='red', size=10), name='Lowest')
    st.plotly_chart(fig, use_container_width=True)
    avg = grouped['bottles_produced'].mean()
    st.markdown(f"**Average Daily Production:** {avg:,.0f} bottles &nbsp; | &nbsp; **Highest:** {max_val:,.0f} on {max_date.date()} &nbsp; | &nbsp; **Lowest:** {min_val:,.0f} on {min_date.date()}")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', title='Defect Rate Trend', labels={'defect_rate': 'Defect Rate (%)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    # Highlight high/low points
    max_val = grouped['defect_rate'].max()
    min_val = grouped['defect_rate'].min()
    max_date = grouped.loc[grouped['defect_rate'].idxmax(), 'date']
    min_date = grouped.loc[grouped['defect_rate'].idxmin(), 'date']
    fig.add_scatter(x=[max_date], y=[max_val], mode='markers', marker=dict(color='green', size=10), name='Highest')
    fig.add_scatter(x=[min_date], y=[min_val], mode='markers', marker=dict(color='red', size=10), name='Lowest')
    st.plotly_chart(fig, use_container_width=True)
    avg = grouped['defect_rate'].mean()
    st.markdown(f"**Average Defect Rate:** {avg:.2f}% &nbsp; | &nbsp; **Highest:** {max_val:.2f}% on {max_date.date()} &nbsp; | &nbsp; **Lowest:** {min_val:.2f}% on {min_date.date()}")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='Downtime Trend', labels={'downtime': 'Downtime (mins)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    max_val = grouped['downtime'].max()
    min_val = grouped['downtime'].min()
    max_date = grouped.loc[grouped['downtime'].idxmax(), 'date']
    min_date = grouped.loc[grouped['downtime'].idxmin(), 'date']
    fig.add_scatter(x=[max_date], y=[max_val], mode='markers', marker=dict(color='green', size=10), name='Highest')
    fig.add_scatter(x=[min_date], y=[min_val], mode='markers', marker=dict(color='red', size=10), name='Lowest')
    st.plotly_chart(fig, use_container_width=True)
    avg = grouped['downtime'].mean()
    st.markdown(f"**Average Downtime:** {avg:.1f} mins &nbsp; | &nbsp; **Highest:** {max_val:.1f} mins on {max_date.date()} &nbsp; | &nbsp; **Lowest:** {min_val:.1f} mins on {min_date.date()}")

def show_shift_breakdown(df):
    st.subheader("Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(grouped, x='shift', y='Defect %', title='Defect % by Shift', text=grouped['Defect %'].round(2).astype(str) + '%')
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    high_shift = grouped.loc[grouped['Defect %'].idxmax()]
    low_shift = grouped.loc[grouped['Defect %'].idxmin()]
    avg = grouped['Defect %'].mean()
    st.markdown(f"**Average Defect %:** {avg:.2f}% &nbsp; | &nbsp; **Highest:** {high_shift['Defect %']:.2f}% (Shift {high_shift['shift']}) &nbsp; | &nbsp; **Lowest:** {low_shift['Defect %']:.2f}% (Shift {low_shift['shift']})")

def show_plant_comparison(df):
    st.subheader("Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index().sort_values(by='bottles_produced', ascending=False)
    fig = px.bar(grouped, x='plant', y='bottles_produced', title='Plant-wise Total Production', text=grouped['bottles_produced'].astype(int).astype(str))
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    high_plant = grouped.iloc[0]
    low_plant = grouped.iloc[-1]
    avg = grouped['bottles_produced'].mean()
    st.markdown(f"**Average Plant Output:** {avg:,.0f} bottles &nbsp; | &nbsp; **Highest:** {high_plant['plant']} ({high_plant['bottles_produced']:,.0f}) &nbsp; | &nbsp; **Lowest:** {low_plant['plant']} ({low_plant['bottles_produced']:,.0f})")

def show_kpi_insights(df):
    st.subheader("KPI Highlights")
    if df.empty:
        st.write("No data available for insights.")
        return
    col1, col2 = st.columns(2)
    with col1:
        prod_by_plant = df.groupby('plant')['bottles_produced'].sum().sort_values(ascending=False)
        st.markdown("**Production by Plant (Sorted)**")
        st.dataframe(prod_by_plant.to_frame(), use_container_width=True)
    with col2:
        defect_by_plant = df.groupby('plant')['defect_count'].sum().sort_values(ascending=False)
        st.markdown("**Defects by Plant (Sorted)**")
        st.dataframe(defect_by_plant.to_frame(), use_container_width=True)

    st.markdown("---")
    st.subheader("Daily Plant Leaders")
    # Daily top producer per day
    daily_prod = df.groupby(['date', 'plant'])['bottles_produced'].sum().reset_index()
    top_prod_per_day = daily_prod.loc[daily_prod.groupby('date')['bottles_produced'].idxmax()]
    fig_prod = px.bar(top_prod_per_day, x='date', y='bottles_produced', color='plant', title='Top Producing Plant Each Day')
    st.plotly_chart(fig_prod, use_container_width=True)
    st.markdown("Table: Days where each plant led daily production.")
    st.dataframe(top_prod_per_day[['date', 'plant', 'bottles_produced']])

    # Daily top defect per day
    daily_defects = df.groupby(['date', 'plant'])['defect_count'].sum().reset_index()
    top_defects_per_day = daily_defects.loc[daily_defects.groupby('date')['defect_count'].idxmax()]
    fig_defect = px.bar(top_defects_per_day, x='date', y='defect_count', color='plant', title='Top Defect-Contributing Plant Each Day')
    st.plotly_chart(fig_defect, use_container_width=True)
    st.markdown("Table: Days where each plant had the highest defects.")
    st.dataframe(top_defects_per_day[['date', 'plant', 'defect_count']])

    # Production vs. Defect Rate (insight plot)
    st.markdown("---")
    st.subheader("Production vs Defect Rate Trend")
    merged = df.groupby('date').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    merged['defect_rate'] = (merged['defect_count'] / merged['bottles_produced']) * 100
    fig = px.line(merged, x='date', y=['bottles_produced', 'defect_rate'],
                  labels={'value': 'Value', 'variable': 'Metric'},
                  title='Production and Defect Rate Over Time')
    st.plotly_chart(fig, use_container_width=True)
    avg_prod = merged['bottles_produced'].mean()
    avg_def_rate = merged['defect_rate'].mean()
    st.markdown(f"**Avg Daily Production:** {avg_prod:,.0f} bottles &nbsp; | &nbsp; **Avg Defect Rate:** {avg_def_rate:.2f}%")

    # Downtime by Shift
    st.markdown("---")
    st.subheader("Downtime Contribution by Shift")
    shift_downtime = df.groupby('shift')['downtime'].sum().reset_index()
    fig = px.pie(shift_downtime, values='downtime', names='shift', title='Share of Total Downtime by Shift', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    most = shift_downtime.loc[shift_downtime['downtime'].idxmax()]
    st.markdown(f"**Shift {most['shift']} contributed the most to total downtime.**")

    # Monthly summary table
    st.markdown("---")
    st.subheader("Monthly Summary Table")
    df['month'] = df['date'].dt.to_period('M')
    month_summary = df.groupby('month').agg(
        total_production=('bottles_produced', 'sum'),
        total_defects=('defect_count', 'sum'),
        total_downtime=('downtime', 'sum'),
        days=('date', 'nunique')
    ).reset_index()
    month_summary['defect_rate'] = (month_summary['total_defects'] / month_summary['total_production']) * 100
    st.dataframe(month_summary[['month', 'total_production', 'total_defects', 'defect_rate', 'total_downtime', 'days']].sort_values('month'), use_container_width=True)

    # Heatmap of defect rates
    st.markdown("---")
    st.subheader("Heatmap of Defect Rates by Plant and Shift")
    heatmap_df = df.groupby(['plant', 'shift']).agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    heatmap_df['defect_rate'] = (heatmap_df['defect_count'] / heatmap_df['bottles_produced']) * 100
    heatmap_pivot = heatmap_df.pivot(index='plant', columns='shift', values='defect_rate')
    fig = px.imshow(heatmap_pivot, aspect="auto", color_continuous_scale='Reds', text_auto='.2f',
                    labels=dict(x="Shift", y="Plant", color="Defect Rate (%)"), title="Defect Rate (%) by Plant and Shift")
    st.plotly_chart(fig, use_container_width=True)

    # Correlation: downtime vs. defects
    st.markdown("---")
    st.subheader("Downtime vs. Defects Correlation")
    corr_df = df.groupby('date').agg({'downtime': 'sum', 'defect_count': 'sum'}).reset_index()
    fig = px.scatter(corr_df, x='downtime', y='defect_count', trendline='ols',
                     labels={'downtime': 'Downtime (mins)', 'defect_count': 'Defects'}, title='Daily Downtime vs. Defects')
    st.plotly_chart(fig, use_container_width=True)
    corr = corr_df['downtime'].corr(corr_df['defect_count'])
    st.markdown(f"**Pearson correlation between downtime and defects:** {corr:.2f}")

