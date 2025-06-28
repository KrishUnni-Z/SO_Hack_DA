import streamlit as st
import os
import time
from pipeline import process_all_files, process_file
import viz

# --- Page Configuration ---
st.set_page_config(
    page_title="Factory Metrics Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
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
</style>
""", unsafe_allow_html=True)

# --- Paths ---
raw_data_path = 'data/raw'
processed_data_path = 'data/processed'
os.makedirs(raw_data_path, exist_ok=True)
os.makedirs(processed_data_path, exist_ok=True)

# --- Title & Intro ---
st.title("🏭 Factory Metrics Integration Dashboard")
st.markdown("Unified, real-time manufacturing analytics for all plants. **Upload Excel files below to update your dashboard.**")

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    menu = st.radio("", ["Dashboard", "Upload Data"])

    st.markdown("---")
    st.markdown("## 📂 Data Upload")
    uploaded_file = st.file_uploader("Upload Plant Excel File", type=["xlsx"])
    if uploaded_file:
        with open(os.path.join(raw_data_path, uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ {uploaded_file.name} uploaded successfully.")
        with st.spinner("Processing file..."):
            time.sleep(1)
            process_file(uploaded_file.name)
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

# --- Main Content ---
if menu == "Dashboard":
    if raw_files:
        with st.spinner("Processing existing files..."):
            time.sleep(1)
            process_all_files()
        st.success("All available data processed successfully.")

    df = viz.load_processed_data()
    if not df.empty:
        tabs = st.tabs(["📊 Overall Summary", "📈 Trends & Breakdowns"])

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
            st.markdown("### 🏷️ Plant Comparison")
            viz.show_plant_comparison(df_filtered)

        with tabs[1]:
            st.header("📈 Trends & Breakdowns")

            smoothing = st.checkbox("Show Smoothed Trend Lines", value=True)
            remove_outliers = st.checkbox("Remove Outliers", value=False)

            data = df_filtered.copy()
            if remove_outliers:
                data = data[(abs(data['bottles_produced'] - data['bottles_produced'].mean()) <= (3 * data['bottles_produced'].std()))]

            # --- Group trend charts in columns for compactness ---
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
            st.markdown("**Defect vs Production Scatter**")
            viz.show_defect_vs_production_scatter(data)

    else:
        st.info("No processed data to display. Please upload plant data files.")

elif menu == "Upload Data":
    st.info("Use the sidebar to upload new plant data files.")

# --- Footer ---
st.markdown("---")
st.caption("Made for Summer Open Hackathon 2025.")
