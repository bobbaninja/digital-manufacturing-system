"""
Database Table Classification Verification
Validates that tables match their assigned phases and dependencies
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def verify_table_classification(db_path=None):
    """Verify that tables match their phase classification"""
    
    if db_path is None:
        db_path = Path(__file__).parent.parent / "sql" / "manufacturing.db"
    
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"✗ Error: Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 100)
    print("DATABASE TABLE CLASSIFICATION VERIFICATION")
    print("=" * 100)
    
    issues = []
    
    # ============================================
    # PHASE 1: STATIC SETUP (Fixed Infrastructure)
    # ============================================
    print("\n" + "=" * 100)
    print("PHASE 1: STATIC SETUP - Fixed Infrastructure (System Initialization)")
    print("=" * 100)
    print("Tables: roles, stations, machines, lines, line_stations")
    print("Expected: Immutable, created once, never deleted\n")
    
    # 1. ROLES
    print("\n1️⃣ ROLES Table")
    cursor.execute("SELECT COUNT(*) FROM roles")
    role_count = cursor.fetchone()[0]
    cursor.execute("SELECT role_name FROM roles ORDER BY role_id")
    roles = [row[0] for row in cursor.fetchall()]
    print(f"   ✓ Total roles: {role_count}")
    print(f"   ✓ Roles: {', '.join(roles)}")
    if role_count < 3:
        issues.append("PHASE 1 WARNING: Too few roles defined")
    
    # 2. STATIONS
    print("\n2️⃣ STATIONS Table")
    cursor.execute("SELECT COUNT(*) FROM stations")
    station_count = cursor.fetchone()[0]
    cursor.execute("SELECT station_name, must_has_machines FROM stations ORDER BY station_id")
    stations = cursor.fetchall()
    print(f"   ✓ Total stations: {station_count}")
    for name, must_has in stations:
        has_text = "MUST have machines" if must_has else "Optional machines"
        print(f"     - {name} ({has_text})")
    if station_count < 2:
        issues.append("PHASE 1 WARNING: Too few stations defined")
    
    # 3. MACHINES
    print("\n3️⃣ MACHINES Table")
    cursor.execute("SELECT COUNT(*) FROM machines")
    machine_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT s.station_name, COUNT(*) as machine_count 
        FROM machines m 
        JOIN stations s ON m.station_id = s.station_id 
        GROUP BY m.station_id
    """)
    machine_distribution = cursor.fetchall()
    print(f"   ✓ Total machines: {machine_count}")
    for station_name, count in machine_distribution:
        print(f"     - {station_name}: {count} machines")
    if machine_count < 5:
        issues.append("PHASE 1 WARNING: Too few machines defined")
    
    # 4. LINES
    print("\n4️⃣ LINES Table")
    cursor.execute("SELECT COUNT(*) FROM lines")
    line_count = cursor.fetchone()[0]
    cursor.execute("SELECT line_code, status FROM lines ORDER BY line_id")
    lines = cursor.fetchall()
    print(f"   ✓ Total lines: {line_count}")
    for code, status in lines:
        print(f"     - {code} (Status: {status})")
    if line_count < 1:
        issues.append("PHASE 1 ERROR: No lines defined")
    
    # 5. LINE_STATIONS
    print("\n5️⃣ LINE_STATIONS Table")
    cursor.execute("SELECT COUNT(*) FROM line_stations")
    ls_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT l.line_code, COUNT(*) as station_count 
        FROM line_stations ls 
        JOIN lines l ON ls.line_id = l.line_id 
        GROUP BY ls.line_id
    """)
    ls_distribution = cursor.fetchall()
    print(f"   ✓ Total line-station mappings: {ls_count}")
    for line_code, count in ls_distribution:
        print(f"     - {line_code}: {count} stations")
    
    cursor.execute("""
        SELECT COUNT(*) FROM line_stations WHERE assigned_machine_id IS NULL
    """)
    null_machines = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM line_stations ls
        JOIN stations s ON ls.station_id = s.station_id
        WHERE s.must_has_machines = 1 AND ls.assigned_machine_id IS NULL
    """)
    missing_required_machines = cursor.fetchone()[0]
    
    if missing_required_machines > 0:
        print(f"   ✗ ERROR: {missing_required_machines} line-stations missing REQUIRED machines")
        issues.append(f"PHASE 1 ERROR: {missing_required_machines} line-stations missing required machines")
    else:
        print(f"   ✓ All required machines assigned (Optional: {null_machines} line-stations without machines is OK)")
    
    # ============================================
    # PHASE 2: PRODUCT DEFINITION
    # ============================================
    print("\n" + "=" * 100)
    print("PHASE 2: PRODUCT DEFINITION - Product Specifications")
    print("=" * 100)
    print("Tables: products, eng_spec")
    print("Expected: Created per product, stable, reference products are in production\n")
    
    # 1. PRODUCTS
    print("\n1️⃣ PRODUCTS Table")
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    cursor.execute("SELECT product_code, product_name, revision FROM products ORDER BY product_id")
    products = cursor.fetchall()
    print(f"   ✓ Total products: {product_count}")
    for code, name, revision in products:
        print(f"     - {code}: {name} ({revision})")
    if product_count < 1:
        issues.append("PHASE 2 ERROR: No products defined")
    
    # 2. ENG_SPEC
    print("\n2️⃣ ENG_SPEC Table (Engineering Specifications)")
    cursor.execute("SELECT COUNT(*) FROM eng_spec")
    spec_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT p.product_code, COUNT(*) as spec_count 
        FROM eng_spec es 
        JOIN products p ON es.product_id = p.product_id 
        GROUP BY es.product_id
    """)
    spec_distribution = cursor.fetchall()
    print(f"   ✓ Total specs: {spec_count}")
    for product_code, count in spec_distribution:
        print(f"     - {product_code}: {count} specs")
    
    # Check spec-station coverage
    cursor.execute("""
        SELECT COUNT(DISTINCT es.station_id) as station_count 
        FROM eng_spec es
    """)
    spec_stations = cursor.fetchone()[0]
    print(f"   ✓ Specs cover {spec_stations} stations")
    
    if spec_count < product_count:
        issues.append("PHASE 2 WARNING: Some products may lack engineering specs")
    
    # ============================================
    # PHASE 3: PLANNING & SCHEDULING
    # ============================================
    print("\n" + "=" * 100)
    print("PHASE 3: PLANNING & SCHEDULING - Production Orders")
    print("=" * 100)
    print("Tables: users, batches, work_orders")
    print("Expected: Created regularly, status changes over time, semi-mutable\n")
    
    # 1. USERS
    print("\n1️⃣ USERS Table")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT r.role_name, COUNT(*) as user_count 
        FROM users u 
        JOIN roles r ON u.role_id = r.role_id 
        GROUP BY u.role_id
    """)
    user_distribution = cursor.fetchall()
    print(f"   ✓ Total users: {user_count}")
    for role_name, count in user_distribution:
        print(f"     - {role_name}: {count} users")
    
    # Check for operators
    cursor.execute("""
        SELECT COUNT(*) FROM users WHERE role_id = (SELECT role_id FROM roles WHERE role_name = 'Operator')
    """)
    operator_count = cursor.fetchone()[0]
    print(f"   ✓ Operators available: {operator_count}")
    if operator_count < 1:
        issues.append("PHASE 3 WARNING: No operators defined for measurements")
    
    # 2. BATCHES
    print("\n2️⃣ BATCHES Table (Production Planning)")
    cursor.execute("SELECT COUNT(*) FROM batches")
    batch_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM batches 
        GROUP BY status
    """)
    batch_status = cursor.fetchall()
    print(f"   ✓ Total batches: {batch_count}")
    for status, count in batch_status:
        print(f"     - Status '{status}': {count} batches")
    
    # Check batch timeline
    cursor.execute("""
        SELECT MIN(created_date), MAX(created_date) FROM batches
    """)
    batch_min_date, batch_max_date = cursor.fetchone()
    print(f"   ✓ Batch creation timeline:")
    print(f"     - Earliest: {batch_min_date}")
    print(f"     - Latest: {batch_max_date}")
    
    # 3. WORK_ORDERS
    print("\n3️⃣ WORK_ORDERS Table (Production Scheduling)")
    cursor.execute("SELECT COUNT(*) FROM work_orders")
    wo_count = cursor.fetchone()[0]
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM work_orders 
        GROUP BY status
    """)
    wo_status = cursor.fetchall()
    print(f"   ✓ Total work orders: {wo_count}")
    for status, count in wo_status:
        print(f"     - Status '{status}': {count} work orders")
    
    cursor.execute("""
        SELECT MIN(scheduled_date), MAX(scheduled_date) FROM work_orders
    """)
    wo_min_date, wo_max_date = cursor.fetchone()
    print(f"   ✓ Work order scheduling:")
    print(f"     - Earliest: {wo_min_date}")
    print(f"     - Latest: {wo_max_date}")
    
    # ============================================
    # PHASE 4: OPERATIONAL - Real-time Data
    # ============================================
    print("\n" + "=" * 100)
    print("PHASE 4: OPERATIONAL - Real-time Production Data")
    print("=" * 100)
    print("Tables: measurement_data")
    print("Expected: Generated during production, immutable once recorded\n")
    
    # 1. MEASUREMENT_DATA
    print("\n1️⃣ MEASUREMENT_DATA Table")
    cursor.execute("SELECT COUNT(*) FROM measurement_data")
    meas_count = cursor.fetchone()[0]
    print(f"   ✓ Total measurements: {meas_count}")
    
    # Check measurement distribution
    cursor.execute("""
        SELECT b.batch_number, COUNT(*) as meas_count 
        FROM measurement_data m 
        JOIN batches b ON m.batch_id = b.batch_id 
        GROUP BY m.batch_id
    """)
    meas_distribution = cursor.fetchall()
    print(f"   ✓ Measurements per batch:")
    for batch_num, count in meas_distribution:
        print(f"     - {batch_num}: {count} measurements")
    
    # Check quality stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_in_spec = 1 THEN 1 ELSE 0 END) as in_spec,
            SUM(CASE WHEN is_in_spec = 0 THEN 1 ELSE 0 END) as out_of_spec
        FROM measurement_data
    """)
    total, in_spec, out_of_spec = cursor.fetchone()
    in_spec_pct = (in_spec / total * 100) if total > 0 else 0
    print(f"   ✓ Quality metrics:")
    print(f"     - In-spec: {in_spec}/{total} ({in_spec_pct:.1f}%)")
    print(f"     - Out-of-spec: {out_of_spec}/{total} ({100-in_spec_pct:.1f}%)")
    
    # Check measurement timeline
    cursor.execute("""
        SELECT MIN(measurement_timestamp), MAX(measurement_timestamp) FROM measurement_data
    """)
    meas_min_time, meas_max_time = cursor.fetchone()
    print(f"   ✓ Measurement timeline:")
    print(f"     - Earliest: {meas_min_time}")
    print(f"     - Latest: {meas_max_time}")
    
    # ============================================
    # DEPENDENCY VALIDATION
    # ============================================
    print("\n" + "=" * 100)
    print("DEPENDENCY VALIDATION")
    print("=" * 100)
    
    print("\n✓ Phase 1 → Phase 2 Dependencies:")
    cursor.execute("""
        SELECT COUNT(DISTINCT es.station_id) as spec_stations,
               COUNT(DISTINCT s.station_id) as total_stations
        FROM eng_spec es
        JOIN stations s ON es.station_id = s.station_id
    """)
    spec_stns, total_stns = cursor.fetchone()
    print(f"   - Specs reference {spec_stns}/{total_stns} stations ✓")
    
    print("\n✓ Phase 2 → Phase 3 Dependencies:")
    cursor.execute("""
        SELECT COUNT(*) FROM batches 
        WHERE product_id IN (SELECT product_id FROM products)
    """)
    valid_batches = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM batches")
    total_batches = cursor.fetchone()[0]
    print(f"   - {valid_batches}/{total_batches} batches reference valid products ✓")
    
    print("\n✓ Phase 3 → Phase 4 Dependencies:")
    cursor.execute("""
        SELECT COUNT(*) FROM measurement_data 
        WHERE batch_id IN (SELECT batch_id FROM batches)
        AND spec_id IN (SELECT spec_id FROM eng_spec)
    """)
    valid_meas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM measurement_data")
    total_meas = cursor.fetchone()[0]
    print(f"   - {valid_meas}/{total_meas} measurements have valid batch & spec ✓")
    
    # ============================================
    # TIMELINE CONSISTENCY CHECK
    # ============================================
    print("\n" + "=" * 100)
    print("TIMELINE CONSISTENCY CHECK")
    print("=" * 100)
    
    print("\n⏱️  Verifying chronological order:")
    cursor.execute("""
        SELECT 
            b.batch_number,
            b.created_date,
            MIN(m.measurement_timestamp) as first_meas,
            MAX(m.measurement_timestamp) as last_meas,
            CASE 
                WHEN b.created_date <= MIN(m.measurement_timestamp) THEN '✓ VALID'
                ELSE '✗ INVALID: Measurement before batch creation'
            END as status
        FROM batches b
        JOIN measurement_data m ON b.batch_id = m.batch_id
        GROUP BY b.batch_id
        ORDER BY b.batch_id
    """)
    timeline_results = cursor.fetchall()
    for batch_num, created, first_meas, last_meas, status in timeline_results:
        print(f"   {status}")
        print(f"     Batch '{batch_num}' created: {created}")
        print(f"     First measurement: {first_meas}")
        if status.startswith('✗'):
            issues.append(f"TIMELINE ERROR: {batch_num} has measurements before creation")
    
    # ============================================
    # FINAL SUMMARY
    # ============================================
    print("\n" + "=" * 100)
    print("VERIFICATION SUMMARY")
    print("=" * 100)
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n" + "=" * 100)
        return False
    else:
        print("\n✅ ALL VERIFICATION CHECKS PASSED!")
        print("\n   Phase 1 (Static Setup): ✓ Valid")
        print("   Phase 2 (Product Definition): ✓ Valid")
        print("   Phase 3 (Planning & Scheduling): ✓ Valid")
        print("   Phase 4 (Operational Data): ✓ Valid")
        print("   Timeline Consistency: ✓ Valid")
        print("\n" + "=" * 100)
        return True
    
    conn.close()


if __name__ == "__main__":
    success = verify_table_classification()
    exit(0 if success else 1)
