"""
Migration: Convert sample_reports to reports table
This unifies all session data into a single table for better calendar integration
"""
import sqlite3
import os
from datetime import datetime

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'sage_reports.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if sample_reports table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sample_reports'
        """)
        if not cursor.fetchone():
            print("ℹ️  No sample_reports table found - nothing to migrate")
            return
        
        # Get all sample reports
        cursor.execute("SELECT * FROM sample_reports")
        samples = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(sample_reports)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📊 Found {len(samples)} sample reports to migrate")
        
        migrated_count = 0
        skipped_count = 0
        created_students = []
        
        for sample in samples:
            sample_dict = dict(zip(columns, sample))
            
            student_name = sample_dict.get('student_name')
            session_date = sample_dict.get('session_date')
            content = sample_dict.get('content')
            subject = sample_dict.get('subject')
            duration = sample_dict.get('duration_hours', '1')
            
            if not student_name or not content:
                print(f"  ⚠️  Skipping sample {sample_dict.get('id')} - missing data")
                skipped_count += 1
                continue
            
            # Find or create student
            cursor.execute("SELECT id FROM students WHERE name = ?", (student_name,))
            student_row = cursor.fetchone()
            
            if student_row:
                student_id = student_row[0]
            else:
                # Create new student
                cursor.execute("""
                    INSERT INTO students (name, subject, active)
                    VALUES (?, ?, ?)
                """, (student_name, subject, False))  # Inactive by default for historical
                student_id = cursor.lastrowid
                created_students.append(student_name)
                print(f"  ✨ Created student: {student_name}")
            
            # Parse session_date
            parsed_date = None
            if session_date:
                try:
                    # Try ISO format first
                    parsed_date = datetime.fromisoformat(session_date)
                except:
                    try:
                        # Try common date formats
                        parsed_date = datetime.strptime(session_date, '%Y-%m-%d %H:%M:%S')
                    except:
                        print(f"  ⚠️  Could not parse date: {session_date}")
            
            # Create report in reports table
            cursor.execute("""
                INSERT INTO reports (
                    student_id,
                    session_date,
                    duration_hours,
                    topics_covered,
                    final_report,
                    status,
                    source,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                parsed_date or datetime.now(),
                duration or '1',
                f"{subject} - Uploaded from historical records" if subject else None,
                content,
                'sent',  # All uploaded reports are marked as sent (used for training)
                'uploaded',
                sample_dict.get('uploaded_at') or datetime.now()
            ))
            
            migrated_count += 1
        
        conn.commit()
        
        print(f"\n✅ Migration Complete!")
        print(f"   ✓ Migrated: {migrated_count} reports")
        print(f"   ⊘ Skipped: {skipped_count} reports")
        if created_students:
            print(f"   ✨ Created {len(created_students)} new students: {', '.join(created_students)}")
        print(f"\n📝 Note: sample_reports table still exists but is no longer used")
        print(f"   You can manually drop it later if desired")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()






