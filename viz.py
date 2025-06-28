import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import zscore
import streamlit as st

def highlight_outliers(series, threshold=3):
    zs = zscore(series, nan_policy='omit')
    return np.abs(zs) > threshold

def show_production_trends(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['bottles_produced'].sum()
    fig = px.line(grouped, x='date', y='bottles_produced', title='📈 Production Trend', labels={'bottles_produced': 'Bottles Produced'})
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    # Highlight outliers
    outliers = highlight_outliers(grouped['bottles_produced'])
    fig.add_scatter(x=grouped.loc[outliers, 'date'], y=grouped.loc[outliers, 'bottles_produced'], mode='markers', marker=dict(color='red', size=8), name='Outlier')
    # Highlight peak and low
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
    # Highlight outliers
    outliers = highlight_outliers(grouped['defect_rate'])
    fig.add_scatter(x=grouped.loc[outliers, 'date'], y=grouped.loc[outliers, 'defect_rate'], mode='markers', marker=dict(color='red', size=8), name='Outlier')
    # Highlight peak and low
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
    # Highlight outliers
    outliers = highlight_outliers(grouped['downtime'])
    fig.add_scatter(x=grouped.loc[outliers, 'date'], y=grouped.loc[outliers, 'downtime'], mode='markers', marker=dict(color='red', size=8), name='Outlier')
    # Highlight peak and low
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
    zs = zscore(df['defect_count'], nan_policy='omit')
    outliers = np.abs(zs) > 3
    fig = px.scatter(
        df, x='bottles_produced', y='defect_count', 
        color=np.where(outliers, 'Outlier', 'Normal'),
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
