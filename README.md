# Factory Metrics Integration Dashboard

A modern web dashboard for unified, real-time analytics across multiple manufacturing plants.  
_Built by Krishnan Unni Prasad for the Summer Open Hackathon 2025._

---

## Overview

This app lets you upload and monitor production, defects, and downtime data for all company plants—live, in one dashboard.  
It provides instant visualisation, cross-plant comparison, and actionable operational insights, with zero Excel wrangling.

**Live Demo:** [sohack25.streamlit.app](https://sohack25.streamlit.app/)

---

## Features

- **Simple Excel upload** — drag and drop `.xlsx` files from any plant, no manual formatting needed
- **Automatic data cleaning and mapping** — adapts to each plant’s column names and structure via [`config/mapping.json`](config/mapping.json)
- **Manual data entry** — easy entry form for plants without Excel output (supports shift as A/B/C or 1/2/3)
- **Instant visual insights** — trends in production, defects, and downtime by day, shift, or plant
- **Live leaderboards and KPIs** — see top and bottom performers, plus key metrics at a glance
- **Built-in correlation and pattern detection** — see links between downtime and defects, all auto-analysed
- **Clear error handling** — immediate, actionable feedback on missing or invalid data
- **Modern interactive UI** — all charts built with Plotly for interactive exploration

---

## How it Works

1. **Upload Excel files** for each plant via the sidebar (`Upload Data` tab)  
2. **Or use manual data entry** (`Manual Entry` tab) for plants that can't export Excel  
3. **App processes, cleans, and maps columns automatically** (see `pipeline.py` and `mapping.json`)
4. **Dashboards auto-update**:
    - **Overall Summary:** KPIs and plant leaderboards
    - **Trends & Breakdowns:** Interactive daily/monthly charts
    - **Insights:** Correlations, shift stats, day-of-week analysis

> **Supported columns:**  
> `date`, `shift`, `bottles_produced`, `defect_count`, `downtime`  
> _(Mapping is automatic if column names differ—see `config/mapping.json`)_

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

## Local Setup

1. **Clone or download this repository**
2. **Install Python 3.9+ and dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
3. **Run the app:**
    ```sh
    streamlit run app.py
    ```
4. **Open your browser at:**  
   [http://localhost:8501](http://localhost:8501)

---

## Edge Cases & FAQ

- **Plant file not mapped in `config/mapping.json`:**  
  The app displays a clear error message.
- **Missing required columns:**  
  The app tells you exactly which columns are missing.
- **Defect count > bottles produced:**  
  Entry is rejected to ensure data validity.
- **Axes auto-scaling:**  
  All charts automatically scale for best comparison.
- **Ordering:**  
  Monthly and day-of-week axes are always displayed in logical order.
- **How to add a new plant/format?**  
  Simply update `config/mapping.json` with the new plant's column mappings.

---

## Author

**Krishnan Unni Prasad**  
Data Science @ University of Technology Sydney  
[sohack25.streamlit.app](https://sohack25.streamlit.app/)

---

_Built for Summer Open Hackathon 2025 – last updated June 2025._
