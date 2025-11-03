"""
Migration: Add next_session_notes column to reports table
"""
import sqlite3
import os

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sage_reports.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add next_session_notes column
        cursor.execute("""
            ALTER TABLE reports 
            ADD COLUMN next_session_notes TEXT
        """)
        
        conn.commit()
        print("✅ Successfully added next_session_notes column to reports table")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️  next_session_notes column already exists - skipping")
        else:
            raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()






