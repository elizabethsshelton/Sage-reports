"""
Migration: Add source column to reports table
"""
import sqlite3
import os

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sage_reports.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add source column
        cursor.execute("""
            ALTER TABLE reports 
            ADD COLUMN source VARCHAR(20) DEFAULT 'created'
        """)
        print("✅ Added source column to reports table")
        
        # Set all existing reports to 'created'
        cursor.execute("""
            UPDATE reports 
            SET source = 'created' 
            WHERE source IS NULL
        """)
        print("✅ Set all existing reports to source='created'")
        
        conn.commit()
        print("✅ Migration completed successfully")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️  source column already exists - skipping")
        else:
            raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()






