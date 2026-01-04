#!/usr/bin/env python3
"""Display current database schema with all tables, columns, and relationships"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "sql" / "manufacturing.db"
db = sqlite3.connect(str(db_path))
c = db.cursor()

print('\n' + '='*100)
print(' '*30 + 'DATABASE SCHEMA - TABLES & RELATIONSHIPS')
print('='*100)

# Get all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in c.fetchall()]

# Get foreign keys for all tables
c.execute("PRAGMA foreign_keys=ON")

for table in tables:
    # Get table info
    c.execute(f"PRAGMA table_info({table})")
    columns = c.fetchall()
    
    c.execute(f"PRAGMA foreign_key_list({table})")
    fks = c.fetchall()
    
    # Get row count
    c.execute(f"SELECT COUNT(*) FROM {table}")
    row_count = c.fetchone()[0]
    
    print(f"\n┌─ TABLE: {table} ({row_count} rows)")
    print(f"│")
    
    for col_id, col_name, col_type, not_null, default_val, pk in columns:
        pk_marker = "🔑 PRIMARY KEY" if pk else ""
        null_marker = "NOT NULL" if not_null else "nullable"
        print(f"│  • {col_name:25} {col_type:12}  {null_marker:15} {pk_marker}")
    
    if fks:
        print(f"│")
        print(f"│  FOREIGN KEYS:")
        for fk in fks:
            fk_col = fk[3]
            ref_table = fk[2]
            ref_col = fk[4]
            print(f"│    → {fk_col:20} references {ref_table}.{ref_col}")
    
    print(f"└")

print('\n' + '='*100)
print('TABLE RELATIONSHIPS (DEPENDENCY GRAPH)')
print('='*100)

# Get all foreign key relationships
relationships = []
for table in tables:
    c.execute(f"PRAGMA foreign_key_list({table})")
    fks = c.fetchall()
    for fk in fks:
        ref_table = fk[2]
        relationships.append((ref_table, table))

if relationships:
    print("\nParent ← Child (Foreign Key)")
    print("-" * 100)
    for parent, child in sorted(set(relationships)):
        print(f"  {parent:25} ← {child:25}")
else:
    print("No relationships found")

print('\n' + '='*100)
print('MANUFACTURING PHASES (LOGICAL GROUPING)')
print('='*100)

phases = {
    "Phase 1: Static Setup (Infrastructure)": ["roles", "stations", "machines", "lines", "line_stations"],
    "Phase 2: Product Definition": ["products", "eng_spec"],
    "Phase 3: Planning & Scheduling": ["users", "batches", "work_orders"],
    "Phase 4: Operational (Quality)": ["measurement_data"]
}

for phase, table_list in phases.items():
    print(f"\n{phase}:")
    for table in table_list:
        if table in tables:
            c.execute(f"SELECT COUNT(*) FROM {table}")
            count = c.fetchone()[0]
            print(f"  ✓ {table:25} {count:6,} rows")

print('\n' + '='*100)
print('DATA SUMMARY')
print('='*100)

total_records = 0
for table in tables:
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    total_records += count
    print(f"  {table:25} {count:6,} rows")

print(f"\n  {'TOTAL':25} {total_records:6,} records")

print('\n' + '='*100 + '\n')

db.close()
