
# Factory Metrics Integration Dashboard

A unified, real-time analytics dashboard for multi-plant manufacturing KPIs. Upload Excel files from your various plants and instantly visualise trends, comparisons, and insights.

## Features

- **One-click upload:** Drag and drop Excel sheets from each plant (template in `/config/mapping.json`).
- **Dynamic, real-time dashboard:** Filter and drill down by plant, shift, date, or week.
- **Automated data cleaning:** Columns are mapped automatically based on your plant and schema.
- **Rich visualisation:** Production, defect, and downtime metrics, with colourful plots and dynamic summary text.
- **Daily/Monthly insights:** See which plant led each day, monthly summaries, and outlier detection.
- **Edge-case handling:** Friendly error messages if a file is missing columns or not mapped.

## Quick Start

### 1. Clone this repo

```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Install dependencies

Recommended: use Python 3.10 or 3.11 (not 3.12+).

```bash
pip install -r requirements.txt
```

### 3. Prepare your data

- Place your Excel files in `data/raw/`.
- File names should be like `plant_1.xlsx`, `plant_2.xlsx`, etc.
- Make sure your columns match one of the templates in `config/mapping.json`.
- Only files for plants listed in mapping.json will be processed (plant_1 to plant_7 by default).

### 4. Run the app

```bash
streamlit run app.py
```

### 5. Using the dashboard

- Use the sidebar to upload or replace plant files.
- If you upload a new file for a plant, it will replace the old one.
- Only 7 plants are allowed—others will show a friendly warning and not crash the app.
- Navigate across tabs for KPIs, breakdowns, and detailed insights.
- Hover plots for more detail; interactive filters let you slice by plant, shift, or date.

## Data Schema

Each plant's Excel file can have unique column names (see `config/mapping.json`). These are mapped automatically to:

- `date`: Production date
- `shift`: A/B/C or 1/2/3 (auto-standardised)
- `bottles_produced`: Units/bottles produced that day/shift
- `defect_count`: Number of rejected/defective units
- `downtime`: Downtime in minutes or hours (as specified in mapping)
- `day_of_week`: Derived automatically

## Troubleshooting

- **Unknown plant?** If you upload a file for a plant not in `mapping.json`, the app shows a clear warning and skips it.
- **Missing columns?** The app reports which required columns are missing in a friendly message.
- **Python version:** This app is tested on Python 3.10–3.11. Some dependencies (like pandas/statsmodels) may not work on 3.12+.
- **Excel format:** Only `.xlsx` files are accepted.

## Credits

Made for Summer Open Hackathon 2025  
Built by [Your Name/Team Name]

---

_This project is a demonstration and not intended for direct deployment in a regulated manufacturing environment._
