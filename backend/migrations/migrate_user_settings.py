"""
Migration: Create user_settings table
"""
import sqlite3
import os

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sage_reports.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create user_settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY,
                tutor_name VARCHAR(100) DEFAULT 'Elizabeth',
                phone VARCHAR(20),
                email VARCHAR(100),
                default_include_contact BOOLEAN DEFAULT 0
            )
        """)
        
        # Insert default profile if table is empty
        cursor.execute("SELECT COUNT(*) FROM user_settings")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("""
                INSERT INTO user_settings (tutor_name, phone, email, default_include_contact)
                VALUES ('Elizabeth', NULL, NULL, 0)
            """)
            print("✅ Created user_settings table with default profile")
        else:
            print("ℹ️  user_settings table already exists")
        
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






