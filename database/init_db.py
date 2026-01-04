"""
Database Initialization Script (New Schema)
Creates the database schema with simplified, flexible manufacturing model
"""

import sqlite3
import os
from pathlib import Path

def init_database(db_path=None):
    """
    Initialize the manufacturing database with complete schema (New Design)
    """
    if db_path is None:
        # Default to sql directory
        db_path = Path(__file__).parent.parent / "sql" / "manufacturing.db"
    
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Delete existing database if it exists (for testing/reset)
    if db_path.exists():
        os.remove(db_path)
        print(f"Removed existing database")
    
    # Read schema file
    schema_path = Path(__file__).parent / "schema.sql"
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Create database and execute schema
    print(f"Creating database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Execute schema
        cursor.executescript(schema_sql)
        conn.commit()
        print("✓ Database schema created successfully")
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Error creating database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Manufacturing MES Database Initialization (New Schema)")
    print("=" * 60)
    
    success = init_database()
    
    if success:
        print("\n" + "=" * 60)
        print("Database initialized successfully!")
        print("Run 'python database/seed_data.py' to populate with sample data")
        print("=" * 60)
    else:
        print("\n✗ Database initialization failed")
