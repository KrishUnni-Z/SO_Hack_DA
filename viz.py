import os
import pandas as pd
import streamlit as st
import plotly.express as px

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
    high_idx = grouped['bottles_produced'].idxmax()
    low_idx = grouped['bottles_produced'].idxmin()
    high_point = grouped.loc[high_idx]
    low_point = grouped.loc[low_idx]
    avg_value = grouped['bottles_produced'].mean()

    fig = px.line(grouped, x='date', y='bottles_produced', title='Production Trend', labels={'bottles_produced': 'Bottles Produced'})
    fig.add_scatter(x=[high_point['date']], y=[high_point['bottles_produced']], mode='markers+text',
                    marker=dict(color='green', size=10), text=["High"], textposition='top center', name='High')
    fig.add_scatter(x=[low_point['date']], y=[low_point['bottles_produced']], mode='markers+text',
                    marker=dict(color='red', size=10), text=["Low"], textposition='bottom center', name='Low')
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Average Daily Production:** {avg_value:,.0f} bottles")
    st.markdown(f"**Highest Production:** {high_point['bottles_produced']:,.0f} on {high_point['date'].date()}")
    st.markdown(f"**Lowest Production:** {low_point['bottles_produced']:,.0f} on {low_point['date'].date()}")

def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    high_idx = grouped['defect_rate'].idxmax()
    low_idx = grouped['defect_rate'].idxmin()
    high_point = grouped.loc[high_idx]
    low_point = grouped.loc[low_idx]
    avg_value = grouped['defect_rate'].mean()

    fig = px.line(grouped, x='date', y='defect_rate', title='Defect Rate Trend', labels={'defect_rate': 'Defect Rate (%)'})
    fig.add_scatter(x=[high_point['date']], y=[high_point['defect_rate']], mode='markers+text',
                    marker=dict(color='green', size=10), text=["High"], textposition='top center', name='High')
    fig.add_scatter(x=[low_point['date']], y=[low_point['defect_rate']], mode='markers+text',
                    marker=dict(color='red', size=10), text=["Low"], textposition='bottom center', name='Low')
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Average Defect Rate:** {avg_value:.2f}%")
    st.markdown(f"**Highest Defect Rate:** {high_point['defect_rate']:.2f}% on {high_point['date'].date()}")
    st.markdown(f"**Lowest Defect Rate:** {low_point['defect_rate']:.2f}% on {low_point['date'].date()}")

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    high_idx = grouped['downtime'].idxmax()
    low_idx = grouped['downtime'].idxmin()
    high_point = grouped.loc[high_idx]
    low_point = grouped.loc[low_idx]
    avg_value = grouped['downtime'].mean()

    fig = px.line(grouped, x='date', y='downtime', title='Downtime Trend', labels={'downtime': 'Downtime (mins)'})
    fig.add_scatter(x=[high_point['date']], y=[high_point['downtime']], mode='markers+text',
                    marker=dict(color='green', size=10), text=["High"], textposition='top center', name='High')
    fig.add_scatter(x=[low_point['date']], y=[low_point['downtime']], mode='markers+text',
                    marker=dict(color='red', size=10), text=["Low"], textposition='bottom center', name='Low')
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Average Downtime:** {avg_value:.1f} mins")
    st.markdown(f"**Highest Downtime:** {high_point['downtime']:.1f} mins on {high_point['date'].date()}")
    st.markdown(f"**Lowest Downtime:** {low_point['downtime']:.1f} mins on {low_point['date'].date()}")

def show_shift_breakdown(df):
    st.subheader("Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(grouped, x='shift', y='Defect %', title='Defect % by Shift')
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def show_plant_comparison(df):
    st.subheader("Total Production by Plant")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index()
    fig = px.bar(grouped, x='plant', y='bottles_produced', title='Total Bottles Produced by Plant')
    st.plotly_chart(fig, use_container_width=True)
    max_plant = grouped.loc[grouped['bottles_produced'].idxmax()]
    min_plant = grouped.loc[grouped['bottles_produced'].idxmin()]
    st.markdown(f"{max_plant['plant']} produced the most overall with {max_plant['bottles_produced']:,} bottles, while {min_plant['plant']} produced the least with {min_plant['bottles_produced']:,} bottles.")

def show_kpi_insights(df):
    st.subheader("Key Performance Indicators (KPIs)")
    if df.empty:
        st.write("No data available for insights.")
        return

    total_bottles = df['bottles_produced'].sum()
    total_defects = df['defect_count'].sum()
    avg_defect_rate = (total_defects / total_bottles) * 100 if total_bottles > 0 else 0
    avg_downtime = df['downtime'].mean()

    st.markdown(f"Total Bottles Produced: **{total_bottles:,.0f}**")
    st.markdown(f"Total Defects: **{total_defects:,.0f}**")
    st.markdown(f"Average Defect Rate: **{avg_defect_rate:.2f}%**")
    st.markdown(f"Average Downtime: **{avg_downtime:.1f} minutes**")

    st.markdown("---")
    st.subheader("Daily Top Plant (Production)")
    daily_prod = df.groupby(['date', 'plant'])['bottles_produced'].sum().reset_index()
    top_prod = daily_prod.loc[daily_prod.groupby('date')['bottles_produced'].idxmax()]
    fig = px.bar(top_prod, x='date', y='bottles_produced', color='plant', title='Top Plant by Production Each Day')
    st.plotly_chart(fig, use_container_width=True)
    top_plant = top_prod['plant'].value_counts().idxmax()
    st.markdown(f"Overall, **{top_plant}** had the most days with top daily production.")

    st.markdown("---")
    st.subheader("Daily Top Plant (Defects)")
    daily_defects = df.groupby(['date', 'plant'])['defect_count'].sum().reset_index()
    top_defect = daily_defects.loc[daily_defects.groupby('date')['defect_count'].idxmax()]
    fig2 = px.bar(top_defect, x='date', y='defect_count', color='plant', title='Top Plant by Defects Each Day')
    st.plotly_chart(fig2, use_container_width=True)
    top_defect_plant = top_defect['plant'].value_counts().idxmax()
    st.markdown(f"Overall, **{top_defect_plant}** had the most days with highest daily defects.")
