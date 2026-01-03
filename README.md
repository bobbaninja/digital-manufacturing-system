# Manufacturing Data Validation Side Project

This project demonstrates data engineering and process optimization skills for a Digital Manufacturing Systems Engineer role. It processes MES events, ERP work orders, and engineering specs to validate measurements, calculate consecutive failures, visualize data, detect alerts, and predict failures.

## Architecture
- **ETL Pipeline**: `etl_pipeline.py` extracts from CSVs, transforms with validations, loads to SQLite.
- **Dashboard**: `dashboard.py` (Streamlit) for visualizations.
- **Alerts**: `alerts.py` checks for thresholds.
- **Prediction**: `predict.py` trains ML model.
- **Viewer**: `view_db.ipynb` notebook to inspect DB.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run ETL: `python python/etl_pipeline.py`
3. View DB: Open `python/view_db.ipynb`
4. Run Dashboard: `streamlit run python/dashboard.py`
5. Run Alerts/Predict: `python python/alerts.py` / `python python/predict.py`

## Data Flow
- Input: CSVs in `data/`
- Output: `sql/manufacturing.db`, `sql/failure_predictor.pkl`

## Improvements Made
- Added `config.py` for paths.
- Implemented logging and error handling.
- Created `requirements.txt`.
- Modularized code into functions.

## Assumptions
- Data is clean; real-world add validation.
- Model is basic; expand with more data/features.