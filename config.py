"""
Manufacturing MES Configuration
Central configuration for database paths, settings, and application constants
"""

import os

# ============================================
# PROJECT PATHS
# ============================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Database
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")
DB_PATH = os.path.join(SQL_DIR, "manufacturing.db")

# Data & Seed Files
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SEED_DIR = os.path.join(DATA_DIR, "seed")

# Application
PYTHON_DIR = os.path.join(PROJECT_ROOT, "python")
PAGES_DIR = os.path.join(PYTHON_DIR, "pages")

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_TIMEOUT = 10  # seconds
DB_CHECK_SAME_THREAD = False

# ============================================
# STREAMLIT CONFIGURATION
# ============================================
STREAMLIT_CONFIG = {
    "page_title": "Manufacturing MES",
    "page_icon": "🏭",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ============================================
# APPLICATION SETTINGS
# ============================================
APP_TITLE = "Manufacturing Execution System (MES)"
APP_VERSION = "2.0"
APP_DESCRIPTION = "Professional manufacturing data dashboard with quality tracking and analytics"

# UI Settings
DEFAULT_PAGE_SIZE = 50
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Quality Metrics
QUALITY_PASS_COLOR = "#28a745"      # Green
QUALITY_FAIL_COLOR = "#dc3545"      # Red
QUALITY_TARGET_PASS_RATE = 0.95     # 95%

# Role Colors (Dashboard Styling)
ROLE_COLORS = {
    "Admin": "#ef553b",              # Red
    "NPI": "#ab63fa",                # Purple
    "Manufacturing": "#636EFA",      # Blue
    "Manager": "#00cc96",            # Green
    "Operator": "#FFA15A"            # Orange
}

# ============================================
# SEED DATA FILES (CSV)
# ============================================
SEED_FILES = {
    "roles": os.path.join(SEED_DIR, "roles.csv"),
    "users": os.path.join(SEED_DIR, "users.csv"),
    "stations": os.path.join(SEED_DIR, "stations.csv"),
    "machines": os.path.join(SEED_DIR, "machines.csv"),
    "lines": os.path.join(SEED_DIR, "lines.csv"),
    "line_stations": os.path.join(SEED_DIR, "line_stations.csv"),
    "products": os.path.join(SEED_DIR, "products.csv"),
    "batches": os.path.join(SEED_DIR, "batches.csv"),
    "work_orders": os.path.join(SEED_DIR, "work_orders.csv"),
    "eng_spec": os.path.join(SEED_DIR, "eng_spec.csv"),
}