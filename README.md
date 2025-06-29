# Factory Metrics Integration Dashboard

A modern web dashboard for unified, real-time analytics across multiple manufacturing plants.  
Built by **Krishnan Unni APrasad** for the Summer Open Hackathon 2025.

---

## Overview

This app enables you to upload and monitor production, defects, and downtime data for multiple plants—all in one place.  
It provides instant visualisation, cross-plant comparison, and operational insights, without any manual Excel work.

**Live Demo:** [sohack25.streamlit.app](https://sohack25.streamlit.app/)

---

## Features

- **Drag-and-drop Excel upload** (.xlsx format)
- **Automated data cleaning and mapping** (`config/mapping.json`)
- **Visualisation:**
    - Production, defects, and downtime trends (daily/monthly)
    - Performance by shift and day of week
    - Plant leaderboards for production and defects
    - KPI highlights and correlation analysis
- **Robust error handling** – clear messages for missing or invalid data
- **Modern interactive UI** – all visualisations built with Plotly

---

## How it Works

1. **Upload Excel files** for each plant via the sidebar (`Upload Data` tab).
2. **The app processes, cleans, and maps columns** automatically (see `pipeline.py` and `mapping.json`).
3. **Dashboards auto-update**, including:
    - **Overall Summary:** Quick KPIs and leaderboards
    - **Trends & Breakdowns:** Interactive charts
    - **Insights:** Correlations, monthly/weekly/shift stats

**Supported columns:**  
- `date`, `shift`, `bottles_produced`, `defect_count`, `downtime`  
(Mapping is automatic even if column names differ—see `config/mapping.json`.)

---

## Project Structure

```
.
├── app.py
├── pipeline.py
├── viz.py
├── config/
│   └── mapping.json
├── data/
│   ├── raw/
│   └── processed/
└── README.md
```

---

## Local Setup

1. **Clone or download this repository.**
2. **Install Python 3.9+ and dependencies:**
    ```
    pip install streamlit plotly pandas openpyxl
    ```
3. **Run the app:**
    ```
    streamlit run app.py
    ```
4. **Open your browser at:**
    ```
    http://localhost:8501
    ```

---

## Edge Cases & FAQ

- **Plant file not mapped in `config/mapping.json`:**  
  The app displays a clear error message.
- **Missing required columns:**  
  The app tells you exactly which columns are missing.
- **Axes auto-scaling:**  
  All charts automatically scale for best comparison.
- **Ordering:**  
  Monthly and day-of-week axes are always displayed in logical order.

---

## Author

**Krishnan Unni APrasad**  
Data Science @ University of Technology Sydney  
[sohack25.streamlit.app](https://sohack25.streamlit.app/)

---

*Built for Summer Open Hackathon 2025. Last updated June 2025.*
