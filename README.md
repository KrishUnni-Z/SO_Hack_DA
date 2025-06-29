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

- **Simple Excel upload** — drag and drop `.xlsx` files from any plant, no manual formatting required
- **Automatic data cleaning and mapping** — adapts to each plant’s column names and structure (`config/mapping.json`)
- **Instant visual insights** — track trends in production, defects, and downtime by day, shift, or plant
- **Live leaderboards and KPIs** — spotlight top and bottom performers, show key metrics at a glance
- **Built-in correlation and pattern detection** — see links between downtime and defects, all auto-analysed
- **Clear error handling** — immediate, actionable feedback on missing or invalid data
- **Modern, interactive UI** — explore all results through fast, interactive Plotly charts


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
    pip install -r requirements.txt
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
