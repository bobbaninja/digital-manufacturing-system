# Schema Changes Reference

## Exact SQL Changes Made

### PRODUCTS Table
```sql
-- NEW COLUMNS ADDED:
ALTER TABLE products ADD COLUMN part_type TEXT CHECK (part_type IN ('composite','metal','assembly','other')) DEFAULT 'other';
ALTER TABLE products ADD COLUMN is_critical INTEGER DEFAULT 0 CHECK (is_critical IN (0,1));
```

**Column Definitions**:
- `part_type`: Categorizes product manufacturing type
- `is_critical`: 1 for critical products, 0 for standard

---

### ENG_SPEC Table  
```sql
-- NEW COLUMNS ADDED:
ALTER TABLE eng_spec ADD COLUMN nominal REAL;
ALTER TABLE eng_spec ADD COLUMN spec_revision TEXT DEFAULT 'Rev A';
```

**Column Definitions**:
- `nominal`: Target/nominal measurement value
- `spec_revision`: Document version (e.g., Rev A, Rev B)

---

### WORK_ORDERS Table
```sql
-- NEW COLUMNS ADDED:
ALTER TABLE work_orders ADD COLUMN due_date DATE;

-- CONSTRAINT ADDED:
ALTER TABLE work_orders MODIFY status TEXT CHECK (status IN ('Scheduled','Released','In Process','Completed','On Hold','Cancelled'));
```

**Column Definitions**:
- `due_date`: Target completion deadline
- `status`: Now limited to 6 valid values (was free-form text)

---

### MEASUREMENT_DATA Table
```sql
-- NEW COLUMN ADDED:
ALTER TABLE measurement_data ADD COLUMN pass_fail TEXT CHECK (pass_fail IN ('PASS','FAIL')) NOT NULL;
```

**Column Definition**:
- `pass_fail`: Explicit PASS/FAIL indicator (derived from is_in_spec)

---

## Updated CREATE TABLE Statements

### PRODUCTS (Updated)
```sql
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
```

### ENG_SPEC (Updated)
```sql
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
```

### WORK_ORDERS (Updated)
```sql
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
```

### MEASUREMENT_DATA (Updated)
```sql
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
```

---

## Column Summary

| Table | Column | Type | Default | Constraint | Purpose |
|-------|--------|------|---------|-----------|---------|
| products | part_type | TEXT | 'other' | CHECK IN (composite,metal,assembly,other) | Product type classification |
| products | is_critical | INTEGER | 0 | CHECK IN (0,1) | Critical product flag |
| eng_spec | nominal | REAL | NULL | None | Target measurement value |
| eng_spec | spec_revision | TEXT | 'Rev A' | None | Spec document version |
| work_orders | due_date | DATE | NULL | None | Deadline tracking |
| work_orders | status | TEXT | 'Scheduled' | CHECK IN (6 values) | Enhanced validation |
| measurement_data | pass_fail | TEXT | NULL | CHECK IN (PASS,FAIL), NOT NULL | Explicit pass/fail status |

---

## Seed Data Population

### Products
```python
# Determine criticality based on product
is_critical = 1 if 'Drone' in row['product_name'] else 0
part_type = row.get('part_type', 'composite')
```

### Eng_Spec
```python
# Calculate nominal as midpoint
nominal = (row['lower_limit'] + row['upper_limit']) / 2
spec_revision = 'Rev A'
```

### Work_Orders
```python
# Set due_date 3 days after scheduled_date
due_date = (datetime.strptime(wo_date, '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d')
status in ('Scheduled', 'Released', 'In Process', 'Completed', 'On Hold', 'Cancelled')
```

### Measurement_Data
```python
# Derive pass_fail from is_in_spec
pass_fail = 'PASS' if is_in_spec == 1 else 'FAIL'
```

---

## No Longer Supported (Removed)

The following were removed during schema redesign in previous sessions:
- `audit_trail` table (consolidated into measurement_data)
- `process_checks` table (renamed to `eng_spec`)

---

## Implementation Status

**All changes implemented and tested**: ✅

- [x] Schema modifications in schema.sql
- [x] Seed data updates in seed_data.py
- [x] Database reinitialized
- [x] Data populated (320 records)
- [x] Queries tested and verified
- [x] Dashboard functional
