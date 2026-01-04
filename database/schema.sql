-- Manufacturing MES Database Schema (Redesigned)
-- Simplified with flexible line-based production scheduling

-- ============================================
-- ROLES & USERS (Simplified)
-- ============================================

CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    role_id INTEGER NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

-- ============================================
-- STATIONS & MACHINES
-- ============================================

CREATE TABLE IF NOT EXISTS stations (
    station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_name TEXT UNIQUE NOT NULL,
    description TEXT,
    must_has_machines BOOLEAN DEFAULT 1,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS machines (
    machine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id INTEGER NOT NULL,
    machine_code TEXT UNIQUE NOT NULL,
    machine_name TEXT NOT NULL,
    brand TEXT,
    status TEXT DEFAULT 'Active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- ============================================
-- MANUFACTURING LINES
-- ============================================

CREATE TABLE IF NOT EXISTS lines (
    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_code TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'Active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS line_stations (
    line_station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    sequence_order INTEGER NOT NULL,
    assigned_machine_id INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (line_id) REFERENCES lines(line_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id),
    FOREIGN KEY (assigned_machine_id) REFERENCES machines(machine_id),
    UNIQUE(line_id, sequence_order)
);

-- ============================================
-- PRODUCTS & BATCHES
-- ============================================

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT UNIQUE NOT NULL,
    product_code TEXT UNIQUE NOT NULL,
    description TEXT,
    category TEXT,
    revision TEXT,
    part_type TEXT CHECK (part_type IN ('composite','metal','assembly','other')) DEFAULT 'other',
    is_critical INTEGER DEFAULT 0 CHECK (is_critical IN (0,1)),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS batches (
    batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_number TEXT UNIQUE NOT NULL,
    product_id INTEGER NOT NULL,
    quantity_planned INTEGER NOT NULL,
    quantity_completed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Pending',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_date TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ============================================
-- WORK ORDERS (Daily Production Scheduling)
-- ============================================

CREATE TABLE IF NOT EXISTS work_orders (
    work_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_number TEXT UNIQUE NOT NULL,
    batch_id INTEGER NOT NULL,
    line_id INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    due_date DATE,
    status TEXT CHECK (status IN ('Scheduled','Released','In Process','Completed','On Hold','Cancelled')) DEFAULT 'Scheduled',
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
    FOREIGN KEY (line_id) REFERENCES lines(line_id)
);

-- ============================================
-- ENGINEERING SPECIFICATIONS (formerly process_checks)
-- ============================================

CREATE TABLE IF NOT EXISTS eng_spec (
    spec_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    check_name TEXT NOT NULL,
    parameter_name TEXT NOT NULL,
    lower_limit REAL NOT NULL,
    upper_limit REAL NOT NULL,
    target_value REAL,
    nominal REAL,
    unit TEXT,
    check_type TEXT,
    is_critical BOOLEAN DEFAULT 0,
    spec_revision TEXT DEFAULT 'Rev A',
    sampling_frequency TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

-- ============================================
-- QUALITY MEASUREMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS measurement_data (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    spec_id INTEGER NOT NULL,
    line_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    machine_id INTEGER,
    measured_value REAL NOT NULL,
    is_in_spec BOOLEAN NOT NULL,
    pass_fail TEXT CHECK (pass_fail IN ('PASS','FAIL')) NOT NULL,
    deviation_percent REAL,
    operator_id INTEGER,
    measurement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
    FOREIGN KEY (spec_id) REFERENCES eng_spec(spec_id),
    FOREIGN KEY (line_id) REFERENCES lines(line_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id),
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    FOREIGN KEY (operator_id) REFERENCES users(user_id)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_machines_station ON machines(station_id);
CREATE INDEX IF NOT EXISTS idx_line_stations_line ON line_stations(line_id);
CREATE INDEX IF NOT EXISTS idx_line_stations_station ON line_stations(station_id);
CREATE INDEX IF NOT EXISTS idx_line_stations_machine ON line_stations(assigned_machine_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_batch ON work_orders(batch_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_line ON work_orders(line_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_date ON work_orders(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_eng_spec_product ON eng_spec(product_id);
CREATE INDEX IF NOT EXISTS idx_eng_spec_station ON eng_spec(station_id);
CREATE INDEX IF NOT EXISTS idx_measurement_data_batch ON measurement_data(batch_id);
CREATE INDEX IF NOT EXISTS idx_measurement_data_line ON measurement_data(line_id);
CREATE INDEX IF NOT EXISTS idx_measurement_data_machine ON measurement_data(machine_id);
