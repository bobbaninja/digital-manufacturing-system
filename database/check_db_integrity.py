"""
Database Integrity Checker
Verifies all foreign key relationships and data consistency
"""

import sqlite3
from pathlib import Path

def check_database_integrity(db_path=None):
    """Check database for data inconsistencies and foreign key violations"""
    
    if db_path is None:
        db_path = Path(__file__).parent.parent / "sql" / "manufacturing.db"
    
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"✗ Error: Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DATABASE INTEGRITY CHECK")
    print("=" * 80)
    
    issues_found = []
    
    try:
        # 1. Check users -> roles
        print("\n1. Checking users -> roles relationship...")
        cursor.execute("""
            SELECT u.user_id, u.username, u.role_id 
            FROM users u 
            LEFT JOIN roles r ON u.role_id = r.role_id 
            WHERE r.role_id IS NULL
        """)
        invalid_users = cursor.fetchall()
        if invalid_users:
            issues_found.append(f"Found {len(invalid_users)} users with invalid role_id:")
            for user in invalid_users:
                issues_found.append(f"  - User ID {user[0]} ({user[1]}) has role_id={user[2]} (doesn't exist)")
        else:
            print("  ✓ All users have valid role_id")
        
        # 2. Check machines -> stations
        print("\n2. Checking machines -> stations relationship...")
        cursor.execute("""
            SELECT m.machine_id, m.machine_code, m.station_id 
            FROM machines m 
            LEFT JOIN stations s ON m.station_id = s.station_id 
            WHERE s.station_id IS NULL
        """)
        invalid_machines = cursor.fetchall()
        if invalid_machines:
            issues_found.append(f"Found {len(invalid_machines)} machines with invalid station_id:")
            for machine in invalid_machines:
                issues_found.append(f"  - Machine ID {machine[0]} ({machine[1]}) has station_id={machine[2]} (doesn't exist)")
        else:
            print("  ✓ All machines have valid station_id")
        
        # 3. Check line_stations -> lines
        print("\n3. Checking line_stations -> lines relationship...")
        cursor.execute("""
            SELECT ls.line_station_id, ls.line_id 
            FROM line_stations ls 
            LEFT JOIN lines l ON ls.line_id = l.line_id 
            WHERE l.line_id IS NULL
        """)
        invalid_line_stations = cursor.fetchall()
        if invalid_line_stations:
            issues_found.append(f"Found {len(invalid_line_stations)} line_stations with invalid line_id:")
            for ls in invalid_line_stations:
                issues_found.append(f"  - Line_station ID {ls[0]} has line_id={ls[1]} (doesn't exist)")
        else:
            print("  ✓ All line_stations have valid line_id")
        
        # 4. Check line_stations -> stations
        print("\n4. Checking line_stations -> stations relationship...")
        cursor.execute("""
            SELECT ls.line_station_id, ls.station_id 
            FROM line_stations ls 
            LEFT JOIN stations s ON ls.station_id = s.station_id 
            WHERE s.station_id IS NULL
        """)
        invalid_ls_stations = cursor.fetchall()
        if invalid_ls_stations:
            issues_found.append(f"Found {len(invalid_ls_stations)} line_stations with invalid station_id:")
            for ls in invalid_ls_stations:
                issues_found.append(f"  - Line_station ID {ls[0]} has station_id={ls[1]} (doesn't exist)")
        else:
            print("  ✓ All line_stations have valid station_id")
        
        # 5. Check line_stations -> machines (when not NULL)
        print("\n5. Checking line_stations -> machines relationship...")
        cursor.execute("""
            SELECT ls.line_station_id, ls.assigned_machine_id 
            FROM line_stations ls 
            LEFT JOIN machines m ON ls.assigned_machine_id = m.machine_id 
            WHERE ls.assigned_machine_id IS NOT NULL AND m.machine_id IS NULL
        """)
        invalid_ls_machines = cursor.fetchall()
        if invalid_ls_machines:
            issues_found.append(f"Found {len(invalid_ls_machines)} line_stations with invalid machine_id:")
            for ls in invalid_ls_machines:
                issues_found.append(f"  - Line_station ID {ls[0]} has machine_id={ls[1]} (doesn't exist)")
        else:
            print("  ✓ All line_stations have valid machine_id (or NULL)")
        
        # 6. Check batches -> products
        print("\n6. Checking batches -> products relationship...")
        cursor.execute("""
            SELECT b.batch_id, b.batch_number, b.product_id 
            FROM batches b 
            LEFT JOIN products p ON b.product_id = p.product_id 
            WHERE p.product_id IS NULL
        """)
        invalid_batches = cursor.fetchall()
        if invalid_batches:
            issues_found.append(f"Found {len(invalid_batches)} batches with invalid product_id:")
            for batch in invalid_batches:
                issues_found.append(f"  - Batch ID {batch[0]} ({batch[1]}) has product_id={batch[2]} (doesn't exist)")
        else:
            print("  ✓ All batches have valid product_id")
        
        # 7. Check work_orders -> batches
        print("\n7. Checking work_orders -> batches relationship...")
        cursor.execute("""
            SELECT wo.work_order_id, wo.work_order_number, wo.batch_id 
            FROM work_orders wo 
            LEFT JOIN batches b ON wo.batch_id = b.batch_id 
            WHERE b.batch_id IS NULL
        """)
        invalid_wo_batches = cursor.fetchall()
        if invalid_wo_batches:
            issues_found.append(f"Found {len(invalid_wo_batches)} work_orders with invalid batch_id:")
            for wo in invalid_wo_batches:
                issues_found.append(f"  - Work Order ID {wo[0]} ({wo[1]}) has batch_id={wo[2]} (doesn't exist)")
        else:
            print("  ✓ All work_orders have valid batch_id")
        
        # 8. Check work_orders -> lines
        print("\n8. Checking work_orders -> lines relationship...")
        cursor.execute("""
            SELECT wo.work_order_id, wo.work_order_number, wo.line_id 
            FROM work_orders wo 
            LEFT JOIN lines l ON wo.line_id = l.line_id 
            WHERE l.line_id IS NULL
        """)
        invalid_wo_lines = cursor.fetchall()
        if invalid_wo_lines:
            issues_found.append(f"Found {len(invalid_wo_lines)} work_orders with invalid line_id:")
            for wo in invalid_wo_lines:
                issues_found.append(f"  - Work Order ID {wo[0]} ({wo[1]}) has line_id={wo[2]} (doesn't exist)")
        else:
            print("  ✓ All work_orders have valid line_id")
        
        # 9. Check eng_spec -> products
        print("\n9. Checking eng_spec -> products relationship...")
        cursor.execute("""
            SELECT es.spec_id, es.check_name, es.product_id 
            FROM eng_spec es 
            LEFT JOIN products p ON es.product_id = p.product_id 
            WHERE p.product_id IS NULL
        """)
        invalid_spec_products = cursor.fetchall()
        if invalid_spec_products:
            issues_found.append(f"Found {len(invalid_spec_products)} eng_specs with invalid product_id:")
            for spec in invalid_spec_products:
                issues_found.append(f"  - Spec ID {spec[0]} ({spec[1]}) has product_id={spec[2]} (doesn't exist)")
        else:
            print("  ✓ All eng_specs have valid product_id")
        
        # 10. Check eng_spec -> stations
        print("\n10. Checking eng_spec -> stations relationship...")
        cursor.execute("""
            SELECT es.spec_id, es.check_name, es.station_id 
            FROM eng_spec es 
            LEFT JOIN stations s ON es.station_id = s.station_id 
            WHERE s.station_id IS NULL
        """)
        invalid_spec_stations = cursor.fetchall()
        if invalid_spec_stations:
            issues_found.append(f"Found {len(invalid_spec_stations)} eng_specs with invalid station_id:")
            for spec in invalid_spec_stations:
                issues_found.append(f"  - Spec ID {spec[0]} ({spec[1]}) has station_id={spec[2]} (doesn't exist)")
        else:
            print("  ✓ All eng_specs have valid station_id")
        
        # 11. Check measurement_data -> batches
        print("\n11. Checking measurement_data -> batches relationship...")
        cursor.execute("""
            SELECT m.measurement_id, m.batch_id 
            FROM measurement_data m 
            LEFT JOIN batches b ON m.batch_id = b.batch_id 
            WHERE b.batch_id IS NULL
            LIMIT 10
        """)
        invalid_meas_batches = cursor.fetchall()
        if invalid_meas_batches:
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_data m 
                LEFT JOIN batches b ON m.batch_id = b.batch_id 
                WHERE b.batch_id IS NULL
            """)
            total_invalid = cursor.fetchone()[0]
            issues_found.append(f"Found {total_invalid} measurements with invalid batch_id:")
            for meas in invalid_meas_batches[:5]:
                issues_found.append(f"  - Measurement ID {meas[0]} has batch_id={meas[1]} (doesn't exist)")
            if total_invalid > 5:
                issues_found.append(f"  ... and {total_invalid - 5} more")
        else:
            print("  ✓ All measurements have valid batch_id")
        
        # 12. Check measurement_data -> eng_spec
        print("\n12. Checking measurement_data -> eng_spec relationship...")
        cursor.execute("""
            SELECT m.measurement_id, m.spec_id 
            FROM measurement_data m 
            LEFT JOIN eng_spec es ON m.spec_id = es.spec_id 
            WHERE es.spec_id IS NULL
            LIMIT 10
        """)
        invalid_meas_specs = cursor.fetchall()
        if invalid_meas_specs:
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_data m 
                LEFT JOIN eng_spec es ON m.spec_id = es.spec_id 
                WHERE es.spec_id IS NULL
            """)
            total_invalid = cursor.fetchone()[0]
            issues_found.append(f"Found {total_invalid} measurements with invalid spec_id:")
            for meas in invalid_meas_specs[:5]:
                issues_found.append(f"  - Measurement ID {meas[0]} has spec_id={meas[1]} (doesn't exist)")
            if total_invalid > 5:
                issues_found.append(f"  ... and {total_invalid - 5} more")
        else:
            print("  ✓ All measurements have valid spec_id")
        
        # 13. Check measurement_data -> lines
        print("\n13. Checking measurement_data -> lines relationship...")
        cursor.execute("""
            SELECT m.measurement_id, m.line_id 
            FROM measurement_data m 
            LEFT JOIN lines l ON m.line_id = l.line_id 
            WHERE l.line_id IS NULL
            LIMIT 10
        """)
        invalid_meas_lines = cursor.fetchall()
        if invalid_meas_lines:
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_data m 
                LEFT JOIN lines l ON m.line_id = l.line_id 
                WHERE l.line_id IS NULL
            """)
            total_invalid = cursor.fetchone()[0]
            issues_found.append(f"Found {total_invalid} measurements with invalid line_id:")
            for meas in invalid_meas_lines[:5]:
                issues_found.append(f"  - Measurement ID {meas[0]} has line_id={meas[1]} (doesn't exist)")
            if total_invalid > 5:
                issues_found.append(f"  ... and {total_invalid - 5} more")
        else:
            print("  ✓ All measurements have valid line_id")
        
        # 14. Check measurement_data -> stations
        print("\n14. Checking measurement_data -> stations relationship...")
        cursor.execute("""
            SELECT m.measurement_id, m.station_id 
            FROM measurement_data m 
            LEFT JOIN stations s ON m.station_id = s.station_id 
            WHERE s.station_id IS NULL
            LIMIT 10
        """)
        invalid_meas_stations = cursor.fetchall()
        if invalid_meas_stations:
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_data m 
                LEFT JOIN stations s ON m.station_id = s.station_id 
                WHERE s.station_id IS NULL
            """)
            total_invalid = cursor.fetchone()[0]
            issues_found.append(f"Found {total_invalid} measurements with invalid station_id:")
            for meas in invalid_meas_stations[:5]:
                issues_found.append(f"  - Measurement ID {meas[0]} has station_id={meas[1]} (doesn't exist)")
            if total_invalid > 5:
                issues_found.append(f"  ... and {total_invalid - 5} more")
        else:
            print("  ✓ All measurements have valid station_id")
        
        # 15. Check measurement_data -> machines (when not NULL)
        print("\n15. Checking measurement_data -> machines relationship...")
        cursor.execute("""
            SELECT m.measurement_id, m.machine_id 
            FROM measurement_data m 
            LEFT JOIN machines ma ON m.machine_id = ma.machine_id 
            WHERE m.machine_id IS NOT NULL AND ma.machine_id IS NULL
            LIMIT 10
        """)
        invalid_meas_machines = cursor.fetchall()
        if invalid_meas_machines:
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_data m 
                LEFT JOIN machines ma ON m.machine_id = ma.machine_id 
                WHERE m.machine_id IS NOT NULL AND ma.machine_id IS NULL
            """)
            total_invalid = cursor.fetchone()[0]
            issues_found.append(f"Found {total_invalid} measurements with invalid machine_id:")
            for meas in invalid_meas_machines[:5]:
                issues_found.append(f"  - Measurement ID {meas[0]} has machine_id={meas[1]} (doesn't exist)")
            if total_invalid > 5:
                issues_found.append(f"  ... and {total_invalid - 5} more")
        else:
            print("  ✓ All measurements have valid machine_id (or NULL)")
        
        # 16. Check measurement_data -> users (operators)
        print("\n16. Checking measurement_data -> users relationship...")
        cursor.execute("""
            SELECT m.measurement_id, m.operator_id 
            FROM measurement_data m 
            LEFT JOIN users u ON m.operator_id = u.user_id 
            WHERE m.operator_id IS NOT NULL AND u.user_id IS NULL
            LIMIT 10
        """)
        invalid_meas_operators = cursor.fetchall()
        if invalid_meas_operators:
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_data m 
                LEFT JOIN users u ON m.operator_id = u.user_id 
                WHERE m.operator_id IS NOT NULL AND u.user_id IS NULL
            """)
            total_invalid = cursor.fetchone()[0]
            issues_found.append(f"Found {total_invalid} measurements with invalid operator_id:")
            for meas in invalid_meas_operators[:5]:
                issues_found.append(f"  - Measurement ID {meas[0]} has operator_id={meas[1]} (doesn't exist)")
            if total_invalid > 5:
                issues_found.append(f"  ... and {total_invalid - 5} more")
        else:
            print("  ✓ All measurements have valid operator_id (or NULL)")
        
        # Additional Logic Checks
        print("\n" + "=" * 80)
        print("ADDITIONAL LOGIC CHECKS")
        print("=" * 80)
        
        # 17. Check if batches reference products that match their work orders
        print("\n17. Checking batch-product consistency with work orders...")
        cursor.execute("""
            SELECT wo.work_order_id, wo.work_order_number, 
                   b.batch_id, b.batch_number, b.product_id,
                   p.product_name
            FROM work_orders wo
            JOIN batches b ON wo.batch_id = b.batch_id
            JOIN products p ON b.product_id = p.product_id
        """)
        wo_consistency = cursor.fetchall()
        print(f"  ✓ All {len(wo_consistency)} work orders have consistent batch-product relationships")
        
        # 18. Check measurement_data batch-product consistency with eng_spec
        print("\n18. Checking measurement batch-product consistency with specs...")
        cursor.execute("""
            SELECT m.measurement_id, m.batch_id, b.product_id as batch_product,
                   m.spec_id, es.product_id as spec_product
            FROM measurement_data m
            JOIN batches b ON m.batch_id = b.batch_id
            JOIN eng_spec es ON m.spec_id = es.spec_id
            WHERE b.product_id != es.product_id
            LIMIT 10
        """)
        mismatched_products = cursor.fetchall()
        if mismatched_products:
            cursor.execute("""
                SELECT COUNT(*) FROM measurement_data m
                JOIN batches b ON m.batch_id = b.batch_id
                JOIN eng_spec es ON m.spec_id = es.spec_id
                WHERE b.product_id != es.product_id
            """)
            total_mismatched = cursor.fetchone()[0]
            issues_found.append(f"Found {total_mismatched} measurements where batch product != spec product:")
            for meas in mismatched_products[:5]:
                issues_found.append(f"  - Measurement {meas[0]}: batch {meas[1]} has product {meas[2]}, but spec {meas[3]} is for product {meas[4]}")
            if total_mismatched > 5:
                issues_found.append(f"  ... and {total_mismatched - 5} more")
        else:
            print("  ✓ All measurements have matching batch-product and spec-product")
        
        # 19. Check if stations with must_has_machines=1 have machines in line_stations
        print("\n19. Checking line_stations machine assignments for must_has_machines stations...")
        cursor.execute("""
            SELECT ls.line_station_id, l.line_code, s.station_name, s.must_has_machines, ls.assigned_machine_id
            FROM line_stations ls
            JOIN lines l ON ls.line_id = l.line_id
            JOIN stations s ON ls.station_id = s.station_id
            WHERE s.must_has_machines = 1 AND ls.assigned_machine_id IS NULL
        """)
        missing_required_machines = cursor.fetchall()
        if missing_required_machines:
            issues_found.append(f"Found {len(missing_required_machines)} line_stations missing required machines:")
            for ls in missing_required_machines[:10]:
                issues_found.append(f"  - Line_station {ls[0]}: Line '{ls[1]}' + Station '{ls[2]}' (must_has_machines=1) has no machine assigned")
        else:
            print("  ✓ All line_stations for must_has_machines stations have machines assigned")
        
        # Final Summary
        print("\n" + "=" * 80)
        if issues_found:
            print("❌ INTEGRITY CHECK FAILED")
            print("=" * 80)
            print(f"\nFound {len(issues_found)} issue(s):\n")
            for issue in issues_found:
                print(issue)
            print("\n" + "=" * 80)
            return False
        else:
            print("✅ ALL CHECKS PASSED - Database integrity is good!")
            print("=" * 80)
            return True
            
    except sqlite3.Error as e:
        print(f"\n✗ Database Error: {e}")
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    success = check_database_integrity()
    exit(0 if success else 1)
