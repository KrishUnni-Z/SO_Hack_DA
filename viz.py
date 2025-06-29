import os
import pandas as pd
import streamlit as st
import plotly.express as px

def blue_box(text):
    st.markdown(f"""
        <div style="
            background-color: #b8dafc;  /* Much more noticeable blue */
            border-left: 6px solid #2196F3;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(33,150,243,0.15);
            padding: 18px 22px;
            margin-bottom: 18px;
            font-size: 1.1rem;
            color: #0d47a1;  /* Deep blue text for contrast */
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-weight: 500;
            line-height: 1.5;
        ">
            {text}
        </div>
    """, unsafe_allow_html=True)


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
    fig = px.line(grouped, x='date', y='bottles_produced', 
                  title='Production Trend by Date', labels={'bottles_produced': 'Bottles Produced'})
    if smoothing:
        grouped['7-day Avg'] = grouped['bottles_produced'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg = grouped['bottles_produced'].mean()
    max_v = grouped['bottles_produced'].max()
    max_date = grouped.loc[grouped['bottles_produced'].idxmax(), 'date'].date()
    min_v = grouped['bottles_produced'].min()
    min_date = grouped.loc[grouped['bottles_produced'].idxmin(), 'date'].date()
    blue_box(
        f"On average, {avg:,.0f} bottles were produced per day. "
        f"The highest daily production was {max_v:,} on {max_date}, "
        f"and the lowest was {min_v:,} on {min_date}."
    )

    st.info("Average daily downtime was 370.1 minutes. Highest was 586.5 mins on 2025-03-24, lowest was 189.6 mins on 2025-02-28.")


def show_defect_rate_trend(df, smoothing=True):
    grouped = df.groupby('date').agg({'defect_count': 'sum', 'bottles_produced': 'sum'}).reset_index()
    grouped['defect_rate'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.line(grouped, x='date', y='defect_rate', 
                  title='Defect Rate Trend by Date', labels={'defect_rate': 'Defect Rate (%)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['defect_rate'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg = grouped['defect_rate'].mean()
    max_v = grouped['defect_rate'].max()
    max_date = grouped.loc[grouped['defect_rate'].idxmax(), 'date'].date()
    min_v = grouped['defect_rate'].min()
    min_date = grouped.loc[grouped['defect_rate'].idxmin(), 'date'].date()
    blue_box(
        f"Average defect rate was {avg:.2f}%. "
        f"Highest defect rate was {max_v:.2f}% on {max_date}, "
        f"and lowest was {min_v:.2f}% on {min_date}."
    )

def show_downtime_trend(df, smoothing=True):
    grouped = df.groupby('date', as_index=False)['downtime'].sum()
    fig = px.line(grouped, x='date', y='downtime', title='Downtime Trend by Date', labels={'downtime': 'Downtime (mins)'})
    if smoothing:
        grouped['7-day Avg'] = grouped['downtime'].rolling(window=7, min_periods=1).mean()
        fig.add_scatter(x=grouped['date'], y=grouped['7-day Avg'], mode='lines', name='7-day Avg', line=dict(dash='dash'))
    st.plotly_chart(fig, use_container_width=True)
    avg = grouped['downtime'].mean()
    max_v = grouped['downtime'].max()
    max_date = grouped.loc[grouped['downtime'].idxmax(), 'date'].date()
    min_v = grouped['downtime'].min()
    min_date = grouped.loc[grouped['downtime'].idxmin(), 'date'].date()
    blue_box(
        f"Average daily downtime was {avg:.1f} minutes. "
        f"Highest was {max_v:.1f} mins on {max_date}, lowest was {min_v:.1f} mins on {min_date}."
    )

def show_shift_breakdown(df):
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
    blue_box(
        f"Shift {max_shift} had the highest defect percentage overall, while shift {min_shift} had the lowest defect percentage."
    )

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
    blue_box(
        f"The plant with the highest total bottle production was **{max_plant.replace('_', ' ').title()}**, while the lowest production was recorded at **{min_plant.replace('_', ' ').title()}**."
    )

def show_dayofweek_production(df):
    st.subheader("Average Production by Day of Week")
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    prod = df.groupby('day_of_week')['bottles_produced'].mean().reindex(dow_order)
    fig = px.bar(
        x=prod.index, y=prod.values, 
        labels={'x': 'Day of Week', 'y': 'Avg Bottles Produced'},
        title="Avg Production by Day"
    )
    st.plotly_chart(fig, use_container_width=True)
    max_day = prod.idxmax()
    min_day = prod.idxmin()
    blue_box(
        f"Production was highest on {max_day} and lowest on {min_day}."
    )

def show_dayofweek_defects(df):
    st.subheader("Average Defects by Day of Week")
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    defects = df.groupby('day_of_week')['defect_count'].mean().reindex(dow_order)
    fig = px.bar(
        x=defects.index, y=defects.values, 
        labels={'x': 'Day of Week', 'y': 'Avg Defect Count'},
        title="Avg Defects by Day"
    )
    st.plotly_chart(fig, use_container_width=True)
    max_day = defects.idxmax()
    min_day = defects.idxmin()
    blue_box(
        f"Defects were highest on {max_day} and lowest on {min_day}."
    )

def show_downtime_contribution_by_shift(df):
    st.subheader("Downtime Contribution by Shift")
    grouped = df.groupby('shift')['downtime'].sum().reset_index()
    fig = px.pie(grouped, names='shift', values='downtime', title='Share of Total Downtime by Shift')
    st.plotly_chart(fig, use_container_width=True)
    top_shift = grouped.loc[grouped['downtime'].idxmax(), 'shift']
    blue_box(f"Shift {top_shift} contributed the most to total downtime in minutes.")

def show_heatmap_defect_rates(df):
    st.subheader("Defect Rates by Plant and Shift")
    pivot = df.pivot_table(index='plant', columns='shift', values='defect_count', aggfunc='sum').fillna(0)
    fig = px.imshow(
        pivot, text_auto=True, aspect="auto", color_continuous_scale='Reds',
        labels={'color': 'Defects'}, title="Total Defects by Plant & Shift"
    )
    st.plotly_chart(fig, use_container_width=True)
    plant_max = pivot.sum(axis=1).idxmax()
    shift_max = pivot.sum().idxmax()
    blue_box(f"Most total defects came from plant {plant_max} and shift {shift_max}.")

def show_monthly_summary_table(df):
    st.subheader("Monthly Summary Table")
    df['month'] = df['date'].dt.strftime('%Y-%m')
    summary = df.groupby('month').agg({
        'bottles_produced': 'mean',
        'defect_count': 'mean',
        'downtime': 'mean'
    }).rename(columns={
        'bottles_produced': 'Avg Production',
        'defect_count': 'Avg Defects',
        'downtime': 'Avg Downtime (mins)'
    }).reset_index()
    st.dataframe(summary, use_container_width=True)
    blue_box(f"Monthly averages calculated across {df['date'].nunique()} unique production days.")

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
    blue_box(f"Pearson correlation between daily downtime and defects: {corr_val:.2f}")

