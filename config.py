import os

# Project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MES_CSV = os.path.join(DATA_DIR, "mes_events.csv")
ERP_CSV = os.path.join(DATA_DIR, "erp_work_orders.csv")
SPECS_CSV = os.path.join(DATA_DIR, "eng_specs.csv")

# SQL paths
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")
DB_PATH = os.path.join(SQL_DIR, "manufacturing.db")
MODEL_PATH = os.path.join(SQL_DIR, "failure_predictor.pkl")

# Python scripts
PYTHON_DIR = os.path.join(PROJECT_ROOT, "python")