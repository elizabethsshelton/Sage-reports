"""
Database migration script to add duration_hours field to reports table
Run this once to update your existing database schema
"""

import sqlite3
import os

def migrate_database(db_path='database/sage_reports.db'):
    """Add duration_hours column to reports table"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"📊 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(reports)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    if 'duration_hours' in existing_columns:
        print("⏭️  Column 'duration_hours' already exists, skipping migration")
        conn.close()
        return True
    
    try:
        cursor.execute("ALTER TABLE reports ADD COLUMN duration_hours VARCHAR(20) DEFAULT '1'")
        conn.commit()
        print(f"✅ Added column: duration_hours")
        
        # Update existing records to have '1' as default
        cursor.execute("UPDATE reports SET duration_hours = '1' WHERE duration_hours IS NULL")
        conn.commit()
        print(f"✅ Updated {cursor.rowcount} existing records with duration_hours='1'")
        
    except sqlite3.OperationalError as e:
        print(f"⚠️  Could not add duration_hours: {e}")
        conn.close()
        return False
    
    conn.close()
    
    print(f"\n✨ Database migration complete!")
    return True


if __name__ == '__main__':
    import sys
    
    # Allow custom database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'database/sage_reports.db'
    
    print("🔄 Sage Reports Database Migration - Add Duration")
    print("=" * 50)
    
    success = migrate_database(db_path)
    
    if success:
        print("\n✅ Migration complete! Restart your backend server.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)


