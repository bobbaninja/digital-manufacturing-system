"""
Database Seed Script
Loads sample data from CSV files into the database (Redesigned Schema)
"""

import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

def seed_database(db_path=None, seed_data_dir=None):
    """
    Seed the database with sample data from CSV files (New Schema)
    
    Args:
        db_path: Path to database file (default: sql/manufacturing.db)
        seed_data_dir: Path to seed data directory (default: data/seed/)
    """
    # Set default paths
    if db_path is None:
        db_path = Path(__file__).parent.parent / "sql" / "manufacturing.db"
    
    if seed_data_dir is None:
        seed_data_dir = Path(__file__).parent.parent / "data" / "seed"
    
    db_path = Path(db_path)
    seed_data_dir = Path(seed_data_dir)
    
    # Verify paths exist
    if not db_path.exists():
        print(f"✗ Error: Database file not found at {db_path}")
        print("  Run database/init_db.py first to create the database.")
        return False
    
    if not seed_data_dir.exists():
        print(f"✗ Error: Seed data directory not found at {seed_data_dir}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("Seeding database with sample data from CSV files...")
        print("=" * 60)
        
        # 1. Load Roles
        print("\n1. Loading roles from CSV...")
        roles_file = seed_data_dir / "roles.csv"
        if roles_file.exists():
            roles_df = pd.read_csv(roles_file)
            for _, row in roles_df.iterrows():
                cursor.execute("""
                    INSERT INTO roles (role_name, description)
                    VALUES (?, ?)
                """, (row['role_name'], row['description']))
            print(f"  ✓ Created {len(roles_df)} roles")
        else:
            print(f"  ⚠ Warning: {roles_file.name} not found")
        
        # 2. Load Users
        print("\n2. Loading users from CSV...")
        users_file = seed_data_dir / "users.csv"
        if users_file.exists():
            users_df = pd.read_csv(users_file)
            for _, row in users_df.iterrows():
                cursor.execute("""
                    INSERT INTO users (username, email, role_id)
                    VALUES (?, ?, ?)
                """, (row['username'], row['email'], row['role_id']))
            print(f"  ✓ Created {len(users_df)} users")
        else:
            print(f"  ⚠ Warning: {users_file.name} not found")
        
        # 3. Load Stations
        print("\n3. Loading stations from CSV...")
        stations_file = seed_data_dir / "stations.csv"
        if stations_file.exists():
            stations_df = pd.read_csv(stations_file)
            for _, row in stations_df.iterrows():
                cursor.execute("""
                    INSERT INTO stations (station_name, description, must_has_machines)
                    VALUES (?, ?, ?)
                """, (row['station_name'], row['description'], row.get('must_has_machines', 1)))
            print(f"  ✓ Created {len(stations_df)} stations")
        else:
            print(f"  ⚠ Warning: {stations_file.name} not found")
        
        # 4. Load Machines
        print("\n4. Loading machines from CSV...")
        machines_file = seed_data_dir / "machines.csv"
        if machines_file.exists():
            machines_df = pd.read_csv(machines_file)
            for _, row in machines_df.iterrows():
                brand = row.get('brand') if pd.notna(row.get('brand')) else None
                cursor.execute("""
                    INSERT INTO machines (station_id, machine_code, machine_name, brand, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['station_id'], row['machine_code'], row['machine_name'], brand, row.get('status', 'Active')))
            print(f"  ✓ Created {len(machines_df)} machines")
        else:
            print(f"  ⚠ Warning: {machines_file.name} not found")
        
        # 5. Load Lines
        print("\n5. Loading manufacturing lines from CSV...")
        lines_file = seed_data_dir / "lines.csv"
        if lines_file.exists():
            lines_df = pd.read_csv(lines_file)
            for _, row in lines_df.iterrows():
                cursor.execute("""
                    INSERT INTO lines (line_code, status)
                    VALUES (?, ?)
                """, (row['line_code'], row.get('status', 'Active')))
            print(f"  ✓ Created {len(lines_df)} lines")
        else:
            print(f"  ⚠ Warning: {lines_file.name} not found")
        
        # 6. Load Line Stations
        print("\n6. Loading line-station assignments from CSV...")
        line_stations_file = seed_data_dir / "line_stations.csv"
        if line_stations_file.exists():
            line_stations_df = pd.read_csv(line_stations_file)
            for _, row in line_stations_df.iterrows():
                machine_id = row.get('assigned_machine_id') if pd.notna(row.get('assigned_machine_id')) else None
                cursor.execute("""
                    INSERT INTO line_stations (line_id, station_id, sequence_order, assigned_machine_id)
                    VALUES (?, ?, ?, ?)
                """, (row['line_id'], row['station_id'], row['sequence_order'], machine_id))
            print(f"  ✓ Created {len(line_stations_df)} line-station assignments")
        else:
            print(f"  ⚠ Warning: {line_stations_file.name} not found")
        
        # 7. Load Products
        print("\n7. Loading products from CSV...")
        products_file = seed_data_dir / "products.csv"
        if products_file.exists():
            products_df = pd.read_csv(products_file)
            for _, row in products_df.iterrows():
                # Determine part_type based on product - assemblies are 'assembly', otherwise 'composite'
                part_type = row.get('part_type', 'composite')
                # First product (DW-1000) is critical, second is standard
                is_critical = 1 if 'Drone' in row['product_name'] else 0
                
                cursor.execute("""
                    INSERT INTO products (product_name, product_code, description, category, revision, part_type, is_critical)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (row['product_name'], row['product_code'], row['description'], 
                      row['category'], row['revision'], part_type, is_critical))
            print(f"  ✓ Created {len(products_df)} products")
        else:
            print(f"  ⚠ Warning: {products_file.name} not found")
        
        # 8. Load Batches
        print("\n8. Loading batches from CSV...")
        batches_file = seed_data_dir / "batches.csv"
        if batches_file.exists():
            batches_df = pd.read_csv(batches_file)
            # Create batches with realistic creation dates (7-10 days ago)
            batch_creation_dates = {}
            for idx, row in batches_df.iterrows():
                # Stagger batch creation dates
                days_ago = 10 - (idx * 2)  # 10, 8, 6, 4 days ago
                created_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
                batch_creation_dates[row['batch_number']] = created_date
                
                cursor.execute("""
                    INSERT INTO batches (batch_number, product_id, quantity_planned, quantity_completed, status, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (row['batch_number'], row['product_id'], row['quantity_planned'], 
                      row.get('quantity_completed', 0), row['status'], created_date))
            print(f"  ✓ Created {len(batches_df)} batches")
        else:
            print(f"  ⚠ Warning: {batches_file.name} not found")
            batch_creation_dates = {}
        
        # 9. Load Work Orders
        print("\n9. Loading work orders from CSV...")
        work_orders_file = seed_data_dir / "work_orders.csv"
        if work_orders_file.exists():
            work_orders_df = pd.read_csv(work_orders_file)
            for _, row in work_orders_df.iterrows():
                # Set work order creation date same as scheduled date
                wo_date = row['scheduled_date']
                # Set due_date to 3 days after scheduled date
                due_date = (datetime.strptime(wo_date, '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d')
                cursor.execute("""
                    INSERT INTO work_orders (work_order_number, batch_id, line_id, scheduled_date, due_date, status, notes, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (row['work_order_number'], row['batch_id'], row['line_id'], 
                      wo_date, due_date, row.get('status', 'Scheduled'), row.get('notes', ''), wo_date))
            print(f"  ✓ Created {len(work_orders_df)} work orders")
        else:
            print(f"  ⚠ Warning: {work_orders_file.name} not found")
        
        # 10. Load Engineering Specifications
        print("\n10. Loading engineering specifications from CSV...")
        eng_spec_file = seed_data_dir / "eng_spec.csv"
        if eng_spec_file.exists():
            eng_spec_df = pd.read_csv(eng_spec_file)
            for _, row in eng_spec_df.iterrows():
                # Calculate nominal value as midpoint of spec limits
                nominal = (row['lower_limit'] + row['upper_limit']) / 2
                cursor.execute("""
                    INSERT INTO eng_spec 
                    (product_id, station_id, check_name, parameter_name, lower_limit, upper_limit, target_value, 
                     nominal, unit, check_type, is_critical, spec_revision, sampling_frequency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (row['product_id'], row['station_id'], row['check_name'], row['parameter_name'], 
                      row['lower_limit'], row['upper_limit'], row['target_value'],
                      nominal, row['unit'], row['check_type'], row['is_critical'], 'Rev A', row['sampling_frequency']))
            print(f"  ✓ Created {len(eng_spec_df)} engineering specifications")
        else:
            print(f"  ⚠ Warning: {eng_spec_file.name} not found")
        
        # 11. Generate Measurement Data
        print("\n11. Generating measurement data...")
        measurements = []
        
        # Get all batches with their creation dates, specs, and line-station-machine mappings
        cursor.execute("""
            SELECT batch_id, product_id, batch_number, created_date FROM batches
        """)
        batches = cursor.fetchall()
        
        cursor.execute("""
            SELECT spec_id, product_id, station_id, lower_limit, upper_limit, target_value 
            FROM eng_spec
        """)
        specs = cursor.fetchall()
        
        cursor.execute("""
            SELECT DISTINCT ls.line_id, ls.station_id, ls.assigned_machine_id 
            FROM line_stations ls
        """)
        line_station_machines = cursor.fetchall()
        
        # Filter out entries with NULL machine_id and ensure we have valid entries
        line_station_machines_valid = [(l, s, m) for l, s, m in line_station_machines if m is not None]
        
        if not line_station_machines_valid:
            print("  ⚠ Warning: No valid line-station-machine combinations found")
            # Create some default combinations
            cursor.execute("SELECT line_id FROM lines LIMIT 3")
            lines = cursor.fetchall()
            cursor.execute("SELECT station_id FROM stations WHERE must_has_machines = 1")
            stations = cursor.fetchall()
            cursor.execute("SELECT machine_id FROM machines LIMIT 10")
            machines = cursor.fetchall()
            
            line_station_machines_valid = []
            for line_id, in lines:
                for station_id, in stations:
                    if machines:
                        machine_id = random.choice(machines)[0]
                        line_station_machines_valid.append((line_id, station_id, machine_id))
        
        # Get all operator user IDs (role_id = 5)
        cursor.execute("""
            SELECT user_id FROM users WHERE role_id = 5
        """)
        operator_ids = [row[0] for row in cursor.fetchall()]
        
        if not operator_ids:
            operator_ids = [5]  # Default operator if none found
        
        for batch_id, product_id, batch_number, batch_created in batches:
            # Get specs for this product
            product_specs = [s for s in specs if s[1] == product_id]
            
            if not product_specs:
                continue
            
            # Parse batch creation date
            try:
                batch_start_time = datetime.strptime(batch_created, '%Y-%m-%d %H:%M:%S')
            except:
                batch_start_time = datetime.now() - timedelta(days=7)
            
            # Generate measurements starting AFTER batch creation
            # Add 1 hour buffer after batch creation before first measurement
            measurement_start = batch_start_time + timedelta(hours=1)
            
            for i in range(50):  # 50 measurements per batch
                spec = random.choice(product_specs)
                spec_id, _, station_id, lower, upper, target = spec
                
                # 80% in-spec, 20% out-of-spec
                if random.random() < 0.8:
                    value = random.uniform(lower, upper)
                    is_in_spec = 1
                else:
                    if random.random() < 0.5:
                        value = random.uniform(lower * 0.9, lower)
                    else:
                        value = random.uniform(upper, upper * 1.1)
                    is_in_spec = 0
                
                deviation = abs((value - target) / target * 100) if target != 0 else 0
                operator_id = random.choice(operator_ids)
                
                # Pick a random line-station-machine combination
                line_id, _, machine_id = random.choice(line_station_machines_valid)
                
                # Generate varied timestamps - measurements spread over 2-3 days
                # Each measurement is 30-90 minutes apart
                hours_offset = i * random.uniform(0.5, 1.5)
                measurement_time = measurement_start + timedelta(hours=hours_offset)
                
                # Set pass_fail based on is_in_spec
                pass_fail = 'PASS' if is_in_spec == 1 else 'FAIL'
                
                measurements.append((batch_id, spec_id, line_id, station_id, machine_id,
                                   value, is_in_spec, pass_fail, deviation, operator_id, measurement_time.strftime('%Y-%m-%d %H:%M:%S')))
        
        cursor.executemany("""
            INSERT INTO measurement_data 
            (batch_id, spec_id, line_id, station_id, machine_id, measured_value, is_in_spec, pass_fail,
             deviation_percent, operator_id, measurement_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, measurements)
        print(f"  ✓ Generated {len(measurements)} measurements")
        
        conn.commit()
        
        # Print Summary
        print("\n" + "=" * 60)
        print("Database seeded successfully!")
        print("=" * 60)
        print("\nData Summary:")
        
        summary_tables = [
            ('roles', 'Roles'),
            ('users', 'Users'),
            ('stations', 'Stations'),
            ('machines', 'Machines'),
            ('lines', 'Manufacturing Lines'),
            ('line_stations', 'Line-Station Assignments'),
            ('products', 'Products'),
            ('batches', 'Batches'),
            ('work_orders', 'Work Orders'),
            ('eng_spec', 'Engineering Specifications'),
            ('measurement_data', 'Measurements')
        ]
        
        for table, label in summary_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {label:.<30} {count:>6,}")
        
        print("\n" + "=" * 60)
        print("Default Login Credentials:")
        print("=" * 60)
        print("  Admin:           admin")
        print("  NPI Engineer:    alice_smith")
        print("  Mfg Engineer:    bob_jones")
        print("  Manager:         carol_white")
        print("  Operator 1:      david_brown")
        print("  Operator 2:      emma_davis")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n✗ Database Error: {e}")
        conn.rollback()
        return False
    
    except FileNotFoundError as e:
        print(f"\n✗ File Error: {e}")
        return False
    
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Manufacturing MES Database Seeding (New Schema)")
    print("=" * 60)
    
    success = seed_database()
    
    if success:
        print("\n✓ Seeding completed successfully!")
        print("\nNext steps:")
        print("  1. Run: streamlit run python/Welcome.py")
        print("  2. Login with any of the credentials above")
        print("  3. Explore the dashboard and data\n")
    else:
        print("\n✗ Seeding failed. Please check the errors above.\n")
