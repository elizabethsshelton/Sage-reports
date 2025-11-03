"""
Migration: Add teacher column to students table
"""
import sqlite3
import os

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sage_reports.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add teacher column
        cursor.execute("""
            ALTER TABLE students 
            ADD COLUMN teacher VARCHAR(100)
        """)
        
        conn.commit()
        print("✅ Successfully added teacher column to students table")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️  teacher column already exists - skipping")
        else:
            raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()






