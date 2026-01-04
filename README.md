# Manufacturing Dashboard - Digital MES System

A professional Manufacturing Execution System (MES) dashboard showcasing production monitoring, quality analytics, and database management capabilities. Built for demonstration of Digital Manufacturing Systems Engineering skills.

## 🎯 Features
- **Real-time Production Monitoring**: Track active batches, quality rates, and process performance
- **Interactive Analytics**: Plotly-powered visualizations for measurement trends and station performance
- **Role-based Access Control**: Multi-user system with admin, engineer, manager, and operator roles
- **Database Administration**: Admin-only panel for schema inspection and data export
- **Flexible Manufacturing Lines**: Machine-to-station assignments with daily work order scheduling
- **Modern Normalized Schema**: 12-table design matching real-world flexible manufacturing systems

## 🏗️ Architecture

### Multi-Page Streamlit Application
```
python/
├── Welcome.py               # Welcome/Home page
└── pages/
    ├── 1_Login.py           # User authentication
    ├── 2_Dashboard.py       # Main production dashboard
    └── 3_Database_Browser.py # Database management (admin-only)
```

### Database Schema (Redesigned)
- **Users & Roles**: Simplified user management with dedicated roles table
- **Manufacturing Lines**: Flexible line-based production with line → station → machine assignments
- **Work Orders**: Daily batch-to-line scheduling for production planning
- **Quality System**: Station-based quality checks with per-machine measurements
- **Audit Trail**: Complete change history logging

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Initialize Database
```bash
python database/init_db.py    # Create schema
python database/seed_data.py  # Load demo data
```

### Run Application
```bash
cd "path/to/manufacturing-data"
streamlit run python/Welcome.py
```

Access at: http://localhost:8501

### Login Credentials (Demo Mode)
- **Admin**: admin
- **NPI Engineer**: alice_smith
- **Manufacturing Engineer**: bob_jones
- **Manager**: carol_white
- **Operators**: david_brown, emma_davis

*Note: Password authentication disabled for demo purposes*


## 📊 Key Metrics Tracked
- **Production KPIs**: Total measurements, quality rate, active batches, failure counts
- **Quality Analytics**: Per-station quality rates with 0-100% visualization
- **Line Performance**: Production efficiency across manufacturing lines
- **Machine Data**: Equipment-level quality measurements and tracking
- **Batch Status**: Real-time progress monitoring for active production batches

## 🗄️ Database Tables (New Schema)
| Table | Purpose |
|-------|---------|
| `roles` | User roles and permissions |
| `users` | User authentication (username, email, role) |
| `stations` | Manufacturing stations/work centers |
| `machines` | Physical equipment assigned to stations |
| `lines` | Manufacturing production lines |
| `line_stations` | Line-to-station assignments with machine flexibility |
| `products` | Product definitions and codes |
| `batches` | Production batch tracking |
| `work_orders` | Daily batch-to-line scheduling |
| `process_checks` | Quality check parameters and specifications |
| `measurement_data` | Quality measurements with line/machine context |
| `audit_trail` | Complete change history logging |

## 📁 Project Structure
```
manufacturing-data/
├── database/
│   ├── init_db.py           # Database schema creation
│   ├── schema.sql           # SQL schema definition (redesigned)
│   └── seed_data.py         # Demo data population from CSV
├── python/
│   ├── Welcome.py           # Welcome page (main entry)
│   ├── alerts.py            # Alert utilities
│   ├── etl_pipeline.py      # Data processing pipeline
│   ├── predict.py           # Prediction utilities
│   └── pages/
│       ├── 1_Login.py       # User authentication
│       ├── 2_Dashboard.py   # Production dashboard
│       └── 3_Database_Browser.py # Database admin
├── sql/
│   └── manufacturing.db     # SQLite database
├── data/
│   └── seed/                # CSV seed data files
│       ├── roles.csv        # Role definitions
│       ├── users.csv        # User list
│       ├── stations.csv     # Station definitions
│       ├── machines.csv     # Machine assignments
│       ├── lines.csv        # Manufacturing lines
│       ├── line_stations.csv # Line-station-machine mappings
│       ├── products.csv     # Product definitions
│       ├── batches.csv      # Batch definitions
│       ├── work_orders.csv  # Daily production scheduling
│       └── process_checks.csv # Quality check parameters
├── config.py                # Configuration settings
└── requirements.txt         # Python dependencies
```

## 🔄 Data Model

### Manufacturing Flow
```
Products → Batches → Work Orders → Lines
              ↓
           Stations → Machines
              ↓
        Quality Checks → Measurements
```

### Key Design Features
- **Flexible Machine Assignment**: Machines assigned per line-station combination for maintenance/optimization
- **Daily Scheduling**: Work orders enable batch → line scheduling for production planning
- **Simplified Users**: No password storage; role-based access via roles table
- **Per-Line Measurements**: Quality data tied to specific lines and machines for traceability

## 📈 Recent Updates (New Schema)

### Database Changes
- Replaced `product_routing` with flexible `line_stations` model
- Introduced `work_orders` for daily production scheduling
- Added dedicated `roles` table for role management
- Simplified `users` table (username, email, role_id only)
- Added `machines` table with station assignments
- Updated `measurement_data` to include line_id and machine_id

### File Structure Changes
- Moved from hard-coded seed data to CSV-based configuration
- Added `data/seed/` directory with 10 CSV files
- Updated `seed_data.py` to load from CSV files
- Simplified `init_db.py` for new schema setup

## 🛠️ Technologies Used
- **Frontend**: Streamlit (Multi-page app framework)
- **Backend**: Python 3.x
- **Database**: SQLite with normalized schema
- **Visualization**: Plotly Express & Plotly Graph Objects
- **Data Processing**: Pandas

## 👨‍💻 Author
**Jeff Huang**  
Digital Manufacturing Systems Engineer  
📧 bobbaninja@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/jhuang116) | [GitHub](https://bobbaninja.github.io)

---

*For Demonstration Purposes Only - © 2026*
