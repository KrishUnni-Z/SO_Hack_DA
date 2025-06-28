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
    outliers = highlight_outliers(grouped['bottles_produced'])
    fig.add_scatter(x=grouped.loc[outliers, 'date'], y=grouped.loc[outliers, 'bottles_produced'], mode='markers', marker=dict(color='red', size=8), name='Outlier')
    max_val = grouped['bottles_produced'].max()
    min_val = grouped['bottles_produced'].min()
    max_date = grouped.loc[grouped['bottles_produced'].idxmax(), 'date']
    min_date = grouped.loc[grouped['bottles_produced'].idxmin(), 'date']
    fig.add_annotation(x=max_date, y=max_val, text=f"Peak: {max_val:,.0f}", showarrow=True, arrowhead=1, ax=0, ay=-40)
    fig.add_annotation(x=min_date, y=min_val, text=f"Low: {min_val:,.0f}", showarrow=True, arrowhead=1, ax=0, ay=40)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Peak: {max_val:,.0f} on {max_date.date()} | Low: {min_val:,.0f} on {min_date.date()}")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', title='📉 Defect Rate Trend', labels={'defect_rate': 'Defect Rate (%)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    outliers = highlight_outliers(grouped['defect_rate'])
    fig.add_scatter(x=grouped.loc[outliers, 'date'], y=grouped.loc[outliers, 'defect_rate'], mode='markers', marker=dict(color='red', size=8), name='Outlier')
    max_val = grouped['defect_rate'].max()
    min_val = grouped['defect_rate'].min()
    max_date = grouped.loc[grouped['defect_rate'].idxmax(), 'date']
    min_date = grouped.loc[grouped['defect_rate'].idxmin(), 'date']
    fig.add_annotation(x=max_date, y=max_val, text=f"Peak: {max_val:.2f}%", showarrow=True, arrowhead=1, ax=0, ay=-40)
    fig.add_annotation(x=min_date, y=min_val, text=f"Low: {min_val:.2f}%", showarrow=True, arrowhead=1, ax=0, ay=40)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Peak: {max_val:.2f}% on {max_date.date()} | Low: {min_val:.2f}% on {min_date.date()}")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='🕒 Downtime Trend', labels={'downtime': 'Downtime (mins)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    outliers = highlight_outliers(grouped['downtime'])
    fig.add_scatter(x=grouped.loc[outliers, 'date'], y=grouped.loc[outliers, 'downtime'], mode='markers', marker=dict(color='red', size=8), name='Outlier')
    max_val = grouped['downtime'].max()
    min_val = grouped['downtime'].min()
    max_date = grouped.loc[grouped['downtime'].idxmax(), 'date']
    min_date = grouped.loc[grouped['downtime'].idxmin(), 'date']
    fig.add_annotation(x=max_date, y=max_val, text=f"Peak: {max_val:,.1f}", showarrow=True, arrowhead=1, ax=0, ay=-40)
    fig.add_annotation(x=min_date, y=min_val, text=f"Low: {min_val:,.1f}", showarrow=True, arrowhead=1, ax=0, ay=40)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Peak: {max_val:,.1f} mins on {max_date.date()} | Low: {min_val:,.1f} mins on {min_date.date()}")

def show_defect_vs_production_scatter(df):
    st.subheader("🔎 Defect Count vs. Bottles Produced")
    if df.empty:
        st.write("No data available.")
        return
    zs = zscore(df['defect_count'], nan_policy='omit')
    outliers = np.abs(zs) > 3
    if outliers.sum() == 0:
        st.info("No statistical outliers detected in defect count.")
    color_labels = np.where(outliers, 'Outlier', 'Normal')
    fig = px.scatter(
        df, x='bottles_produced', y='defect_count',
        color=color_labels,
        color_discrete_map={'Outlier': 'red', 'Normal': 'blue'},
        title='Defect vs Production Scatter',
        labels={'bottles_produced': 'Bottles Produced', 'defect_count': 'Defect Count'}
    )
    fig.update_layout(legend_title_text='Status')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Red points are statistical outliers (Z-score > 3).")

def show_shift_breakdown(df):
    st.subheader("📊 Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({
        'bottles_produced': 'sum',
        'defect_count': 'sum'
    }).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(
        grouped, x='shift', y='Defect %',
        title='Defect % by Shift',
        labels={'shift': 'Shift', 'Defect %': 'Defect %'}
    )
    fig.update_traces(
        text=grouped['Defect %'].round(2).astype(str) + '%',
        textposition='outside'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Highest: Shift {grouped.loc[grouped['Defect %'].idxmax(), 'shift']} | Lowest: Shift {grouped.loc[grouped['Defect %'].idxmin(), 'shift']}")

def show_plant_comparison(df):
    st.subheader("🏷️ Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig = px.bar(
        grouped, x='plant', y='bottles_produced',
        title='Plant-wise Total Production',
        labels={'plant': 'Plant', 'bottles_produced': 'Total Bottles Produced'}
    )
    fig.update_traces(
        text=grouped['bottles_produced'].astype(int).astype(str),
        textposition='outside'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Highest: {grouped.loc[grouped['bottles_produced'].idxmax(), 'plant']} | Lowest: {grouped.loc[grouped['bottles_produced'].idxmin(), 'plant']}")

def show_kpi_insights(df):
    st.subheader("📌 KPI Insights")
    if df.empty:
        st.write("No data available for insights.")
        return
    prod = df.groupby('date')['bottles_produced'].sum()
    if len(prod) >= 14:
        last_7_avg = prod[-7:].mean()
        prev_7_avg = prod[-14:-7].mean()
        prod_trend = ((last_7_avg - prev_7_avg) / prev_7_avg) * 100 if prev_7_avg != 0 else 0
    else:
        last_7_avg = prod.mean()
        prod_trend = 0
    st.write(f"**Production:** Last 7-day avg: {last_7_avg:,.0f} | Change vs prev week: {prod_trend:+.2f}%")

    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'})
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    defect = grouped['defect_rate']
    if len(defect) >= 14:
        last_7_avg = defect[-7:].mean()
        prev_7_avg = defect[-14:-7].mean()
        defect_trend = ((last_7_avg - prev_7_avg) / prev_7_avg) * 100 if prev_7_avg != 0 else 0
    else:
        last_7_avg = defect.mean()
        defect_trend = 0
    st.write(f"**Defect Rate:** Last 7-day avg: {last_7_avg:.2f}% | Change vs prev week: {defect_trend:+.2f}%")

    downtime = df.groupby('date')['downtime'].sum()
    if len(downtime) >= 14:
        last_7_avg = downtime[-7:].mean()
        prev_7_avg = downtime[-14:-7].mean()
        downtime_trend = ((last_7_avg - prev_7_avg) / prev_7_avg) * 100 if prev_7_avg != 0 else 0
    else:
        last_7_avg = downtime.mean()
        downtime_trend = 0
    st.write(f"**Downtime:** Last 7-day avg: {last_7_avg:.1f} mins | Change vs prev week: {downtime_trend:+.2f}%")

def show_top_days_table(df):
    st.subheader("🏅 Top/Bottom 3 Days")
    prod = df.groupby('date')['bottles_produced'].sum()
    st.write("**Best Production Days:**")
    st.dataframe(prod.sort_values(ascending=False).head(3))
    st.write("**Worst Production Days:**")
    st.dataframe(prod.sort_values().head(3))
