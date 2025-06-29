import streamlit as st
import os
import time
from pipeline import process_all_files, process_file,safe_process_file
import viz
import pandas as pd

ALLOWED_PLANTS = {f"plant_{i}" for i in range(1, 8)}

st.set_page_config(
    page_title="Factory Metrics Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.metric-card {
    background-color: #f5f7fa;
    border-radius: 10px;
    padding: 10px 20px;
    margin: 5px 0;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    text-align: center;
}
.metric-title {
    font-size: 1.2em;
    color: #2e3a59;
    font-weight: 600;
}
.metric-value {
    font-size: 2em;
    color: #0072b5;
    font-weight: 700;
}
.metric-subtitle {
    font-size: 0.9em;
    color: #6c757d;
}
.blue-box {
    background-color: #e6f0fa;
    border-left: 4px solid #0072b5;
    padding: 10px 18px;
    border-radius: 6px;
    margin-top: 8px;
    margin-bottom: 12px;
    font-size: 1em;
}
</style>
""", unsafe_allow_html=True)

raw_data_path = 'data/raw'
processed_data_path = 'data/processed'
os.makedirs(raw_data_path, exist_ok=True)
os.makedirs(processed_data_path, exist_ok=True)

st.title("🏭 Factory Metrics Integration Dashboard")
st.markdown("Unified, real-time manufacturing analytics for all plants. **Upload Excel files below to update your dashboard.**")

with st.sidebar:
    st.markdown("## 🧭 Navigation")
    menu = st.radio("", ["Dashboard", "Upload Data", "Manual Entry"])

    st.markdown("---")
    st.markdown("## 📂 Data Upload")
    uploaded_file = st.file_uploader("Upload Plant Excel File", type=["xlsx"])
    if uploaded_file:
        with open(os.path.join(raw_data_path, uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ {uploaded_file.name} uploaded successfully.")
        with st.spinner("Processing file..."):
            time.sleep(1)
            error = safe_process_file(uploaded_file.name)
        if error:
            st.error(f"❌ File not processed: {error}")
        else:
            st.success("File processed and saved.")

    raw_files = [f for f in os.listdir(raw_data_path) if f.endswith('.xlsx')]
    processed_files = [f for f in os.listdir(processed_data_path) if f.endswith('_clean.csv')]

    if raw_files:
        st.markdown("---")
        st.markdown("### 📄 Loaded Data Files")
        for file in raw_files:
            st.write(f"- {file}")

    if processed_files:
        st.markdown("---")
        st.markdown("### 🗂️ Processed Data by Plant")
        for file in processed_files:
            plant_name = file.replace('_clean.csv', '')
            st.write(f"✅ Processed: {plant_name}")

if menu == "Dashboard":
    with st.spinner("Processing existing files..."):
        time.sleep(1)
        process_all_files()
    st.success("All available data processed successfully.")

    df = viz.load_processed_data()
    if not df.empty:
        tabs = st.tabs(["📊 Overall Summary", "📈 Trends & Breakdowns", "🧠 Insights"])

        with tabs[0]:
            st.header("📊 Overall Summary")
            df_filtered = viz.filter_data(df)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card"><div class="metric-title">Total Plants</div><div class="metric-value">{}</div><div class="metric-subtitle">Active</div></div>'.format(
                    df_filtered['plant'].nunique()), unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card"><div class="metric-title">Total Bottles</div><div class="metric-value">{:,}</div><div class="metric-subtitle">Produced</div></div>'.format(
                    int(df_filtered['bottles_produced'].sum())), unsafe_allow_html=True)
            with col3:
                defect_rate = (df_filtered['defect_count'].sum() / df_filtered['bottles_produced'].sum()) * 100 if df_filtered['bottles_produced'].sum() > 0 else 0
                st.markdown('<div class="metric-card"><div class="metric-title">Defect Rate</div><div class="metric-value">{:.2f}%</div><div class="metric-subtitle">Rejects</div></div>'.format(
                    defect_rate), unsafe_allow_html=True)
            with col4:
                avg_downtime = df_filtered['downtime'].mean()
                st.markdown('<div class="metric-card"><div class="metric-title">Avg Downtime</div><div class="metric-value">{:.1f}</div><div class="metric-subtitle">minutes</div></div>'.format(
                    avg_downtime), unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### Plant Comparison")
            viz.show_plant_comparison(df_filtered)

        with tabs[1]:
            st.header("Trends & Breakdowns")
            smoothing = st.checkbox("Show Smoothed Trend Lines", value=True)
            data = df_filtered.copy()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Production Trend by Date**")
                viz.show_production_trends(data, smoothing=smoothing)
            with col2:
                st.markdown("**Defect Rate Trend by Date**")
                viz.show_defect_rate_trend(data, smoothing=smoothing)

            st.markdown("---")
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("**Downtime Trend by Date**")
                viz.show_downtime_trend(data, smoothing=smoothing)
            with col4:
                st.markdown("**Shift-wise Breakdown**")
                viz.show_shift_breakdown(data)

            st.markdown("---")

        with tabs[2]:
            st.header("Insights & Highlights")
            viz.show_kpi_insights(df_filtered)
            st.markdown("**Day of Week Analysis**")
            col_a, col_b = st.columns(2)
            with col_a:
                viz.show_dayofweek_production(data)
            with col_b:
                viz.show_dayofweek_defects(data)

    else:
        st.info("No processed data to display. Please upload plant data files.")

elif menu == "Upload Data":
    st.info("Use the sidebar to upload new plant data files.")
elif menu == "Manual Entry":
    st.header("Manual Data Entry")
    st.info("Enter new data for any plant below. This is for plants that can't upload Excel files.")

    st.markdown(
        "<small>Shifts can be entered as <b>A, B, C</b> or as <b>1, 2, 3</b>. They will be standardised automatically.</small>",
        unsafe_allow_html=True
    )

    with st.form("manual_entry_form"):
        plant = st.selectbox("Plant", sorted(list(ALLOWED_PLANTS)))
        date = st.date_input("Date")
        shift = st.selectbox("Shift", ["A", "B", "C", "1", "2", "3"])
        bottles_produced = st.number_input("Bottles Produced", min_value=1, value=1)
        defect_count = st.number_input("Defect Count", min_value=0, value=0)
        downtime = st.number_input("Downtime (mins)", min_value=0, value=0)
        submitted = st.form_submit_button("Submit Entry")

    if submitted:
        # Prevent invalid numbers
        if bottles_produced < 1:
            st.error("Bottles produced must be at least 1.")
        elif defect_count < 0 or downtime < 0:
            st.error("Defect count and downtime cannot be negative.")
        elif not plant or not date or not shift:
            st.error("All fields are required.")
        else:
            try:
                # Standardise shift
                shift_map = {'1': 'A', '2': 'B', '3': 'C', 'A': 'A', 'B': 'B', 'C': 'C'}
                shift_std = shift_map.get(str(shift), shift)
                day_of_week = pd.to_datetime(str(date)).day_name()
                entry = pd.DataFrame([{
                    "date": date,
                    "shift": shift_std,
                    "bottles_produced": bottles_produced,
                    "defect_count": defect_count,
                    "downtime": downtime,
                    "day_of_week": day_of_week
                }])
                processed_file = os.path.join(processed_data_path, f"{plant}_clean.csv")
                duplicate = False
                if os.path.exists(processed_file):
                    existing = pd.read_csv(processed_file, parse_dates=['date'])
                    duplicate = (
                        (existing['date'].astype(str) == str(date)) &
                        (existing['shift'] == shift_std)
                    ).any()
                if duplicate:
                    st.warning(f"An entry for {plant} on {date}, shift {shift_std} already exists. Not added.")
                else:
                    entry.to_csv(processed_file, mode='a' if os.path.exists(processed_file) else 'w',
                                 header=not os.path.exists(processed_file), index=False)
                    st.success(f"Entry added for {plant} on {date}, shift {shift_std}.")
                    st.balloons()
                    # Show last 5 entries for that plant
                    recent = pd.read_csv(processed_file, parse_dates=['date']).sort_values('date', ascending=False).head(5)
                    st.markdown("#### Last 5 Entries for this Plant")
                    st.dataframe(recent, use_container_width=True)
            except Exception as e:
                st.error(f"Could not add entry: {e}")


st.markdown("---")
st.caption("Made for Summer Open Hackathon 2025.")
