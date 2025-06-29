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

def _delta_phrase(val, avg, unit=""):
    pct = ((val - avg) / avg) * 100 if avg else 0
    if abs(pct) < 10:
        return f"{val:,.1f}{unit}, close to average"
    elif pct > 50:
        return f"{val:,.1f}{unit}, over 50% above average"
    elif pct > 20:
        return f"{val:,.1f}{unit}, well above average"
    elif pct > 0:
        return f"{val:,.1f}{unit}, a bit above average"
    elif pct < -50:
        return f"{val:,.1f}{unit}, less than half the average"
    elif pct < -20:
        return f"{val:,.1f}{unit}, much lower than average"
    elif pct < 0:
        return f"{val:,.1f}{unit}, a bit below average"
    return f"{val:,.1f}{unit}"

### --- Main Plots ---

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
    st.info(
        f"**Average daily production:** {avg_val:,.0f} bottles.  \n"
        f"**Maximum:** {_delta_phrase(max_val, avg_val, ' bottles')} (on {max_date.strftime('%b %d, %Y')}).  \n"
        f"**Minimum:** {_delta_phrase(min_val, avg_val, ' bottles')} (on {min_date.strftime('%b %d, %Y')})."
    )

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
    st.info(
        f"**Average defect rate:** {avg_val:.2f}%.  \n"
        f"**Highest:** {_delta_phrase(max_val, avg_val, '%')} (on {max_date.strftime('%b %d, %Y')}).  \n"
        f"**Lowest:** {_delta_phrase(min_val, avg_val, '%')} (on {min_date.strftime('%b %d, %Y')})."
    )

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
    st.info(
        f"**Average daily downtime:** {avg_val:.1f} mins.  \n"
        f"**Maximum:** {_delta_phrase(max_val, avg_val, ' mins')} (on {max_date.strftime('%b %d, %Y')}).  \n"
        f"**Minimum:** {_delta_phrase(min_val, avg_val, ' mins')} (on {min_date.strftime('%b %d, %Y')})."
    )

def show_shift_breakdown(df):
    st.subheader("Shift-wise Defect % Breakdown")
    grouped = df.groupby('shift').agg({'bottles_produced': 'sum', 'defect_count': 'sum'}).reset_index()
    grouped['Defect %'] = (grouped['defect_count'] / grouped['bottles_produced']) * 100
    fig = px.bar(
        grouped, x='shift', y='Defect %',
        title='Defect % by Shift',
        labels={'shift': 'Shift', 'Defect %': 'Defect Percentage (%)'},
        color='shift', color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig.update_traces(text=grouped['Defect %'].round(2).astype(str) + '%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    max_shift = grouped.loc[grouped['Defect %'].idxmax(), 'shift']
    min_shift = grouped.loc[grouped['Defect %'].idxmin(), 'shift']
    max_val = grouped['Defect %'].max()
    min_val = grouped['Defect %'].min()
    avg_val = grouped['Defect %'].mean()
    st.info(
        f"**Shift {max_shift}** has the highest defect rate at {max_val:.2f}%, "
        f"which is {((max_val-avg_val)/avg_val)*100:.1f}% above the shift average.  "
        f"**Shift {min_shift}** has the lowest at {min_val:.2f}%."
    )

def show_plant_comparison(df):
    
    st.subheader("Who Led Production Each Day?")
    daily_prod = df.groupby(['date', 'plant'])['bottles_produced'].sum().reset_index()
    daily_prod['leader'] = (daily_prod.groupby('date')['bottles_produced']
                            .transform(lambda x: x == x.max()))
    leaders = daily_prod[daily_prod['leader']]
    fig_leader = px.scatter(
        leaders, x='date', y='bottles_produced', color='plant',
        labels={'bottles_produced': 'Daily Max Produced', 'plant': 'Leader'},
        title='Plant Leading Daily Production'
    )
    st.plotly_chart(fig_leader, use_container_width=True)
    st.info("Shows which plant led daily production. Hover to see the plant and values.")

    st.subheader("Total Production by Plant (Sorted)")
    grouped = df.groupby('plant')['bottles_produced'].sum().reset_index().sort_values(by='bottles_produced', ascending=False)
    fig = px.bar(
        grouped, x='plant', y='bottles_produced',
        title='Total Production by Plant (Sorted)',
        labels={'plant': 'Plant', 'bottles_produced': 'Total Bottles Produced'},
        color='plant', color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(grouped, use_container_width=True)
    max_plant = grouped.iloc[0]['plant']
    min_plant = grouped.iloc[-1]['plant']
    st.info(f"{max_plant} produced the most bottles overall, while {min_plant} produced the least.")

def show_defect_comparison(df):
    
    st.subheader("Who Had Most Defects Each Day?")
    daily_defects = df.groupby(['date', 'plant'])['defect_count'].sum().reset_index()
    daily_defects['leader'] = (daily_defects.groupby('date')['defect_count']
                               .transform(lambda x: x == x.max()))
    defect_leaders = daily_defects[daily_defects['leader']]
    fig_def_leader = px.scatter(
        defect_leaders, x='date', y='defect_count', color='plant',
        labels={'defect_count': 'Daily Max Defects', 'plant': 'Leader'},
        title='Plant with Most Defects Per Day'
    )
    st.plotly_chart(fig_def_leader, use_container_width=True)
    st.info("Shows which plant had the most defects each day. Hover to see values.")

    st.subheader("Total Defects by Plant (Sorted)")
    grouped = df.groupby('plant')['defect_count'].sum().reset_index().sort_values(by='defect_count', ascending=False)
    fig = px.bar(
        grouped, x='plant', y='defect_count',
        title='Total Defects by Plant (Sorted)',
        labels={'plant': 'Plant', 'defect_count': 'Total Defects'},
        color='plant', color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(grouped, use_container_width=True)
    max_plant = grouped.iloc[0]['plant']
    min_plant = grouped.iloc[-1]['plant']
    st.info(f"{max_plant} recorded the highest total defects, {min_plant} the least.")

def show_monthly_metric_trends(df):
    df['month'] = df['date'].dt.to_period('M').astype(str)
    # Production
    st.subheader("Monthly Production by Plant")
    prod_month = df.groupby(['month', 'plant'])['bottles_produced'].sum().reset_index()
    fig1 = px.bar(
        prod_month, x='month', y='bottles_produced', color='plant',
        barmode='group', labels={'bottles_produced': 'Total Produced', 'month': 'Month'},
        title='Monthly Production by Plant', color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig1, use_container_width=True)
    if not prod_month.empty:
        top_prod_month = prod_month.loc[prod_month.groupby('month')['bottles_produced'].idxmax()]
        month = top_prod_month['month'].iloc[-1]
        plant = top_prod_month['plant'].iloc[-1]
        val = top_prod_month['bottles_produced'].iloc[-1]
        st.info(f"In {month}, {plant} led production with {val:,} bottles produced.")

    # Defects
    st.subheader("Monthly Defects by Plant")
    def_month = df.groupby(['month', 'plant'])['defect_count'].sum().reset_index()
    fig2 = px.bar(
        def_month, x='month', y='defect_count', color='plant',
        barmode='group', labels={'defect_count': 'Total Defects', 'month': 'Month'},
        title='Monthly Defects by Plant', color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig2, use_container_width=True)
    if not def_month.empty:
        top_def_month = def_month.loc[def_month.groupby('month')['defect_count'].idxmax()]
        month = top_def_month['month'].iloc[-1]
        plant = top_def_month['plant'].iloc[-1]
        val = top_def_month['defect_count'].iloc[-1]
        st.info(f"In {month}, {plant} had the most defects: {val:,}.")

    # Downtime
    st.subheader("Monthly Downtime by Plant")
    dt_month = df.groupby(['month', 'plant'])['downtime'].sum().reset_index()
    fig3 = px.bar(
        dt_month, x='month', y='downtime', color='plant',
        barmode='group', labels={'downtime': 'Total Downtime (mins)', 'month': 'Month'},
        title='Monthly Downtime by Plant', color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig3, use_container_width=True)
    if not dt_month.empty:
        top_dt_month = dt_month.loc[dt_month.groupby('month')['downtime'].idxmax()]
        month = top_dt_month['month'].iloc[-1]
        plant = top_dt_month['plant'].iloc[-1]
        val = top_dt_month['downtime'].iloc[-1]
        st.info(f"In {month}, {plant} experienced the most downtime: {val:,.0f} mins.")

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
    st.info(f"Most total defects come from plant {plant_max} and shift {shift_max}.")

def show_dayofweek_production(df):
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    prod = df.groupby('day_of_week')['bottles_produced'].mean().reindex(dow_order)
    fig1 = px.bar(
        x=prod.index, y=prod.values, 
        labels={'x': 'Day of Week', 'y': 'Avg Bottles Produced'},
        title="Avg Production by Day",
        color=prod.index, color_discrete_sequence=px.colors.qualitative.Bold
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
        title="Avg Defects by Day",
        color=defects.index, color_discrete_sequence=px.colors.qualitative.Pastel
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
    if not summary.empty:
        month = summary['month'].iloc[-1]
        top_plant = summary['Top Plant'].iloc[-1]
        defect_plant = summary['Most Defects Plant'].iloc[-1]
        st.info(
            f"In {month}: {top_plant} had the highest average production, {defect_plant} saw the most average defects."
        )

def show_kpi_insights(df):
    st.subheader("KPI Highlights")
    if df.empty:
        st.write("No data available for insights.")
        return

    col1, col2 = st.columns(2)
    with col1:
        show_plant_comparison(df)
    with col2:
        show_defect_comparison(df)

    st.markdown("---")
    show_monthly_metric_trends(df)
    st.markdown("---")
    show_heatmap_defect_rates(df)
    st.markdown("---")
    show_downtime_contribution_by_shift(df)
    st.markdown("---")
    show_downtime_defect_correlation(df)
    st.markdown("---")

def show_downtime_contribution_by_shift(df):
    st.subheader("Downtime Contribution by Shift")
    grouped = df.groupby('shift')['downtime'].sum().reset_index()
    fig = px.pie(grouped, names='shift', values='downtime', title='Share of Total Downtime by Shift', color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)
    top_shift = grouped.loc[grouped['downtime'].idxmax(), 'shift']
    st.info(f"Shift {top_shift} contributed the most to total downtime in minutes.")

def show_downtime_defect_correlation(df):
    st.subheader("Downtime vs. Defects Correlation")
    corr_df = df.groupby('date').agg({'downtime': 'sum', 'defect_count': 'sum'}).reset_index()
    fig = px.scatter(
        corr_df, x='downtime', y='defect_count',
        labels={'downtime': 'Downtime (mins)', 'defect_count': 'Defects'},
        title='Daily Downtime vs. Defects',
        trendline="ols", color='defect_count', color_continuous_scale=px.colors.sequential.Bluered
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
