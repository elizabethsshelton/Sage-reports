"""
Migration: Add school field and remove parent_email from students table
"""
import sqlite3
import os

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sage_reports.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add school column
        try:
            cursor.execute("""
                ALTER TABLE students 
                ADD COLUMN school VARCHAR(100)
            """)
            print("✅ Successfully added school column to students table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  school column already exists - skipping")
            else:
                raise e
        
        # Note: SQLite doesn't support DROP COLUMN easily, so we'll just leave parent_email
        # but not use it in the application
        print("ℹ️  parent_email column left in database but will not be used")
        
        conn.commit()
        print("✅ Migration completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()






