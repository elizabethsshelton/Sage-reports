"""
Database migration script to add metadata fields to sample_reports table
Run this once to update your existing database schema
"""

import sqlite3
import os
from datetime import datetime

def migrate_database(db_path='database/sage_reports.db'):
    """Add new columns to sample_reports table"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"📊 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(sample_reports)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    new_columns = {
        'student_name': 'VARCHAR(100)',
        'session_date': 'DATETIME',
        'subject': 'VARCHAR(100)',
        'session_type': 'VARCHAR(100)',
        'duration_hours': 'VARCHAR(20)',
        'attendance_status': 'VARCHAR(50)',
        'source': 'VARCHAR(50) DEFAULT "manual"',
        'learnspeed_session_id': 'VARCHAR(100)'
    }
    
    added_columns = []
    skipped_columns = []
    
    for column_name, column_type in new_columns.items():
        if column_name in existing_columns:
            skipped_columns.append(column_name)
            continue
        
        try:
            cursor.execute(f"ALTER TABLE sample_reports ADD COLUMN {column_name} {column_type}")
            added_columns.append(column_name)
            print(f"✅ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            print(f"⚠️  Could not add {column_name}: {e}")
    
    # Update existing records to have 'manual' as source
    try:
        cursor.execute("UPDATE sample_reports SET source = 'manual' WHERE source IS NULL")
        conn.commit()
        print(f"✅ Updated {cursor.rowcount} existing records with source='manual'")
    except Exception as e:
        print(f"⚠️  Could not update source: {e}")
    
    conn.close()
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Added {len(added_columns)} new columns")
    if skipped_columns:
        print(f"   ⏭️  Skipped {len(skipped_columns)} existing columns")
    print(f"\n✨ Database migration complete!")
    
    return True


if __name__ == '__main__':
    import sys
    
    # Allow custom database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/sage_reports.db'
    
    print("🔄 Sage Reports Database Migration")
    print("=" * 50)
    
    success = migrate_database(db_path)
    
    if success:
        print("\n✅ You can now run the LearnSpeed import script!")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)

